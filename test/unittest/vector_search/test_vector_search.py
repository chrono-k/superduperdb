import tempfile
import uuid

import numpy as np
import pytest

from superduperdb import CFG
from superduperdb.vector_search.base import VectorItem
from superduperdb.vector_search.in_memory import InMemoryVectorSearcher
from superduperdb.vector_search.lance import LanceVectorSearcher


@pytest.fixture
def index_data(monkeypatch):
    with tempfile.TemporaryDirectory() as unique_dir:
        monkeypatch.setattr(CFG, 'lance_home', str(unique_dir))
        h = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
        ids = [str(uuid.uuid4()) for _ in range(h.shape[0])]
        yield h, ids, unique_dir


@pytest.mark.parametrize(
    "vector_index_cls", [InMemoryVectorSearcher, LanceVectorSearcher]
)
@pytest.mark.parametrize("measure", ['l2', 'dot', 'cosine'])
def test_index(index_data, measure, vector_index_cls):
    h, ids, ud = index_data
    h = vector_index_cls(
        identifier='my-index', h=h, index=ids, measure=measure, dimensions=3
    )
    y = np.array([0, 0.5, 0.5])
    res, _ = h.find_nearest_from_array(y, 1)
    assert res[0] == ids[0]

    y = np.array([0.66, 0.66, 0.66])

    h.add([VectorItem(id='new', vector=y)])
    res, _ = h.find_nearest_from_array(y, 1)

    assert res[0] == 'new'
