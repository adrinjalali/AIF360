from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import abstractmethod
from functools import wraps

from aiflearn.datasets import Dataset
from aiflearn.decorating_metaclass import ApplyDecorator


# TODO: Use sklearn.exceptions.NotFittedError instead?
class NotFittedError(ValueError, AttributeError):
    """Error to be raised if `predict` or `transform` is called before `fit`."""

def addmetadata(func):
    """Decorator for instance methods which perform a transformation and return
    a new dataset.

    Automatically populates the `metadata` field of the new dataset to reflect
    details of the transformation that occurred, e.g.::

        {
            'transformer': 'TransformerClass.function_name',
            'params': kwargs_from_init,
            'previous': [all_datasets_used_by_func]
        }
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        new_dataset = func(self, *args, **kwargs)
        if isinstance(new_dataset, Dataset):
            new_dataset.metadata = new_dataset.metadata.copy()
            new_dataset.metadata.update({
                'transformer': '{}.{}'.format(type(self).__name__, func.__name__),
                'params': self._params,
                'previous': [a for a in args if isinstance(a, Dataset)]
            })
        return new_dataset
    return wrapper


BaseClass = ApplyDecorator(addmetadata)

class Transformer(BaseClass):
    """Abstract base class for transformers.

    Transformers are an abstraction for any process which acts on a
    :obj:`Dataset` and returns a new, modified Dataset. This definition
    encompasses pre-processing, in-processing, and post-processing algorithms.
    """

    @abstractmethod
    def __init__(self, **kwargs):
        """Initialize a Transformer object.

        Algorithm-specific configuration parameters should be passed here.
        """
        self._params = kwargs

    def fit(self, dataset):
        """Train a model on the input.

        Args:
            dataset (Dataset): Input dataset.

        Returns:
            Transformer: Returns self.
        """
        return self

    def predict(self, dataset):
        """Return a new dataset with labels predicted by running this
        Transformer on the input.

        Args:
            dataset (Dataset): Input dataset.

        Returns:
            Dataset: Output dataset. `metadata` should reflect the details of
            this transformation.
        """
        raise NotImplementedError("'predict' is not supported for this class. "
            "Perhaps you meant 'transform' or 'fit_predict' instead?")

    def transform(self, dataset):
        """Return a new dataset generated by running this Transformer on the
        input.

        This function could return different `dataset.features`,
        `dataset.labels`, or both.

        Args:
            dataset (Dataset): Input dataset.

        Returns:
            Dataset: Output dataset. `metadata` should reflect the details of
            this transformation.
        """
        raise NotImplementedError("'transform' is not supported for this class."
            " Perhaps you meant 'predict' or 'fit_transform' instead?")

    def fit_predict(self, dataset):
        """Train a model on the input and predict the labels.

        Equivalent to calling `fit(dataset)` followed by `predict(dataset)`.

        Args:
            dataset (Dataset): Input dataset.

        Returns:
            Dataset: Output dataset. `metadata` should reflect the details of
            this transformation.
        """
        return self.fit(dataset).predict(dataset)

    def fit_transform(self, dataset):
        """Train a model on the input and transform the dataset accordingly.

        Equivalent to calling `fit(dataset)` followed by `transform(dataset)`.

        Args:
            dataset (Dataset): Input dataset.

        Returns:
            Dataset: Output dataset. `metadata` should reflect the details of
            this transformation.
        """
        return self.fit(dataset).transform(dataset)