from pydantic import BaseModel, Field

from src.mongo import ModelObjectId


class QuizQuestionWithAnswer(BaseModel):
    tile: str
    answer_options: list[str]
    correct_answer_index: int


class QuizQuestion(BaseModel):
    tile: str
    answer_options: list[str]


class VerifiedCompletion(BaseModel):
    user_id: ModelObjectId
    correct_answers: int
    total_questions: int
    earned_points: int
    completed_timestamp: float


class Quiz(BaseModel):
    id: ModelObjectId = Field(alias="_id")
    title: str
    description: str | None = None
    questions: list[QuizQuestionWithAnswer]
    points_per_answer: int
    verified_completions: list[VerifiedCompletion]


class QuizResponse(BaseModel):
    id: ModelObjectId = Field(alias="_id")
    title: str
    description: str | None = None
    questions: list[QuizQuestion]
    points_per_answer: int
    verified_completion: bool


class QuizAdminResponse(BaseModel):
    id: ModelObjectId = Field(alias="_id")
    title: str
    description: str | None = None
    questions: list[QuizQuestionWithAnswer]
    points_per_answer: int
    verified_completions: list[VerifiedCompletion]


class QuizCreationRequest(BaseModel):
    title: str
    description: str | None = None
    questions: list[QuizQuestionWithAnswer]
    points_per_answer: int


class QuizUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    questions: list[QuizQuestionWithAnswer] | None = None
    points_per_answer: int | None = None


class VerifyCompletionRequest(BaseModel):
    correct_answer_indexes: list[int]


class VerifyCompletionResponse(BaseModel):
    correct_answers: int
    total_questions: int
    earned_points: int
