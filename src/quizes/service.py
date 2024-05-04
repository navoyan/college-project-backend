import time
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from src import mongo
from src.quizes.exceptions import QuizAlreadyCompleted, QuizNotFound
from src.quizes.schemas import (
    Quiz,
    QuizAdminResponse,
    QuizCreationRequest,
    QuizResponse,
    QuizUpdateRequest,
    VerifiedCompletion,
    VerifyCompletionRequest,
    VerifyCompletionResponse,
)
from src.users.exceptions import UserNotFound
from src.users.schemas import User, UserRole


async def find_all_quizes(current_user: User) -> list[QuizResponse | QuizAdminResponse]:
    quiz_dicts = await mongo.quizes_collection.find({}).to_list(None)

    return list(map(lambda quiz_dict: _build_quiz_response(current_user, quiz_dict), quiz_dicts))


async def find_quiz_by_id(current_user: User, id: ObjectId) -> QuizResponse | QuizAdminResponse:
    quiz_dict = await mongo.quizes_collection.find_one({"_id": id})

    if quiz_dict is None:
        raise QuizNotFound

    return _build_quiz_response(current_user, quiz_dict)


def _build_quiz_response(current_user: User, quiz_dict: dict) -> QuizResponse | QuizAdminResponse:
    if current_user.role == UserRole.admin:
        return QuizAdminResponse(**quiz_dict)
    else:
        quiz = Quiz(**quiz_dict)
        verified_completion = any(
            current_user.id == completion.user_id for completion in quiz.verified_completions
        )
        return QuizResponse(verified_completion=verified_completion, **quiz_dict)


async def create_quiz(creation_request: QuizCreationRequest) -> Quiz:
    creation_request_dict = creation_request.model_dump(exclude_unset=True)
    creation_request_dict["verified_completions"] = []
    insert_result = await mongo.quizes_collection.insert_one(creation_request_dict)

    creation_request_dict["_id"] = insert_result.inserted_id
    return Quiz(**creation_request_dict)


async def update_quiz_by_id(id: ObjectId, update: QuizUpdateRequest) -> Quiz:
    update_dict = update.model_dump(exclude_unset=True)

    updated_quiz_dict = await mongo.quizes_collection.find_one_and_update(
        {"_id": id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
    )

    if updated_quiz_dict is None:
        raise QuizNotFound

    return Quiz(**updated_quiz_dict)


async def delete_quiz_by_id(id: ObjectId):
    delete_result = await mongo.quizes_collection.delete_one({"_id": id})

    if delete_result.deleted_count == 0:
        raise QuizNotFound


async def verify_quiz_completion(
    quiz_id: ObjectId, user: User, verified_completion: VerifyCompletionRequest
) -> VerifyCompletionResponse:
    quiz_dict = await mongo.quizes_collection.find_one({"_id": quiz_id})

    if not quiz_dict:
        raise QuizNotFound

    quiz = Quiz(**quiz_dict)

    if any(completion.user_id == user.id for completion in quiz.verified_completions):
        raise QuizAlreadyCompleted

    correct_answers = 0
    for (
        question_index,
        provided_correct_answer_index,
    ) in enumerate(verified_completion.correct_answer_indexes):
        if provided_correct_answer_index == quiz.questions[question_index].correct_answer_index:
            correct_answers += 1

    earned_points = correct_answers * quiz.points_per_answer

    update_result = await mongo.users_collection.update_one(
        {"_id": user.id}, {"$inc": {"points": earned_points}}
    )

    if update_result.modified_count == 0:
        raise UserNotFound

    completion = VerifiedCompletion(
        user_id=user.id,
        correct_answers=correct_answers,
        total_questions=len(quiz.questions),
        earned_points=earned_points,
        completed_timestamp=time.time(),
    )
    completion_dict = completion.model_dump()

    await mongo.quizes_collection.update_one(
        {"_id": quiz_id}, {"$push": {"verified_completions": completion_dict}}
    )

    return VerifyCompletionResponse(**completion_dict)
