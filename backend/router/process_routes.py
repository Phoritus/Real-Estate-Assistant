from fastapi import APIRouter, Request
from controller.process_controller import (
    initialize_process,
    process_urls,
    get_answer,
    AnswerResponse,
    UrlList,
    Query,
)
from rate_limiting import limiter

# --- API Router ---

process_router = APIRouter(
    prefix="/process",
    tags=["process"]
)


@process_router.post("/process-urls", status_code=201)
@limiter.limit("5/minute")
async def process_url_list(payload: UrlList, request: Request):
    initialize_process()
    return process_urls(payload)


@process_router.post("/query", response_model=AnswerResponse)
async def query_answer(payload: Query):
    # call controller function get_answer; avoid returning a coroutine
    return get_answer(payload)



