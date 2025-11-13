from fastapi import APIRouter
from controller.process_controller import (
    initialize_process,
    process_urls,
    get_answer,
    AnswerResponse,
    UrlList,
    Query,
)
from ..rate_limiting import limiter

# --- API Router ---

process_router = APIRouter(
    prefix="/process",
    tags=["process"]
)
@limiter.limit("5/minute")(process_router)

@process_router.post("/initialize", status_code=200)
async def initialize():
    return initialize_process()


@process_router.post("/process-urls", status_code=201)
async def process_url_list(payload: UrlList):
    return process_urls(payload)


@process_router.post("/query", response_model=AnswerResponse)
async def query_answer(payload: Query):
    # call controller function get_answer; avoid returning a coroutine
    return get_answer(payload)



