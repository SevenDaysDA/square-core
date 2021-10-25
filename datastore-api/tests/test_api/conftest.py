import pytest
from app.core.auth import verify_api_key
from app.main import get_app
from app.models.datastore import DatastoreResponse
from app.models.index import Index
from fastapi.testclient import TestClient
from vespa.package import Document, Field, FieldSet, QueryTypeField, Schema


@pytest.fixture(scope="package")
def wiki_schema():
    return Schema(
        "wiki",
        Document(
            fields=[
                Field("title", "string", indexing=["summary", "index"], index="enable-bm25"),
                Field("text", "string", indexing=["summary", "index"], index="enable-bm25"),
                Field("id", "long", indexing=["summary", "attribute"]),
            ]
        ),
        fieldsets=[FieldSet(name="default", fields=["title", "text"])],
    )


@pytest.fixture(scope="package")
def wiki_datastore(wiki_schema):
    return DatastoreResponse.from_vespa(wiki_schema)


@pytest.fixture(scope="package")
def bm25_index():
    return Index(
        datastore_name="wiki",
        name="bm25",
        yql_where_clause="userQuery()",
        embedding_type=None,
        hnsw=None,
        first_phase_ranking="bm25(title) + bm25(text)",
        second_phase_ranking=None,
        bm25=True,
    )


@pytest.fixture(scope="package")
def dpr_index():
    return Index(
        datastore_name="wiki",
        name="dpr",
        yql_where_clause='([{"targetNumHits":100, "hnsw.exploreAdditionalHits":100}]nearestNeighbor(dpr_embedding,dpr_query_embedding)) or userQuery()',
        doc_encoder_model="facebook/dpr-ctx_encoder-single-nq-base",
        query_encoder_model="facebook/dpr-question_encoder-single-nq-base",
        embedding_type="tensor<bfloat16>(x[769])",
        hnsw={"distance_metric": "euclidean", "max_links_per_node": 16, "neighbors_to_explore_at_insert": 500},
        first_phase_ranking="closeness(dpr_embedding)",
        second_phase_ranking=None,
        bm25=False,
        embedding_size=769,
        distance_metric="euclidean",
    )


@pytest.fixture(scope="package")
def dpr_query_type_field():
    return QueryTypeField("ranking.features.query(dpr_query_embedding)", "tensor<float>(x[769])")


@pytest.fixture(scope="package")
def test_document():
    return {
        "id": 1,
        "title": "test document",
        "text": "this is a test document",
    }


@pytest.fixture(scope="package")
def test_document_embedding():
    return [0] * 769


@pytest.fixture(scope="package")
def query_document():
    return {
        "id": 2,
        "title": "document title",
        "text": "document containing the query word quack",
    }


@pytest.fixture(scope="package")
def client():
    app = get_app()
    app.dependency_overrides[verify_api_key] = lambda: True
    client = TestClient(app)
    return client