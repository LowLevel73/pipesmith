# pipesmith

**pipesmith** is a simple Python utility class designed to help you create and validate pipelines by combining different callable objects or steps, each potentially labeled with metadata.

The steps are combined using the Cartesian product, similar to `itertools.product`. Afterward, combinations that do not meet the user-defined conditions are filtered out.

**pipesmith** provides a list of valid combinations of steps, which you can then loop through and execute in your own code.


### Version

Current version: **1.1.0**


## Features

- **Flexible Pipeline Construction:** Combine different callable objects into valid pipelines based on custom conditions.
- **Label-Based Validation:** Apply conditions to ensure certain steps are included, excluded, or required based on the labels associated with the callable object.
- **Input Validation:** Automatically validate the syntax of the input structure during initialization.


## Usage

### Basic Example

Here’s a basic example of how to use the `pipesmith` class to create and validate function combinations.

In this example, we aim to create a pipeline with three steps: a vectorizer, a clusterer, and a sampler. The "tobottomp_sampler" requires the presence of both a vectorizer and a clusterer, while the "random_sampler" can function independently, without requiring any prior steps.

```python
from pipesmith import pipesmith

# Define some example functions
def tfidf_vectorizer(): pass
def count_vectorizer(): pass
def kmeans_clusterer(): pass
def dbscan_clusterer(): pass
def topbottom_sampler(): pass
def random_sampler(): pass

# Define conditions for valid pipelines
conditions = [
    {
        "condition": "skip_if_label",
        "target_step": "sampler",
        "label": {"independent": True},
        "skip_steps": ["vectorizer", "clusterer"]
    },
    {
        "condition": "require_if_label",
        "target_step": "sampler",
        "label": {"name": "topbottom"},
        "required_steps": ["vectorizer", "clusterer"]
    }
]

# Create an instance of pipesmith with steps and conditions
steps = pipesmith(
    ('vectorizer', [
        tfidf_vectorizer,  # No labels
        count_vectorizer,  # No labels
        None  # Optional None to indicate no vectorizer
    ]),
    ('clusterer', [
        kmeans_clusterer,  # No labels
        dbscan_clusterer,  # No labels
        None  # Optional None to indicate no clusterer
    ]),
    ('sampler', [
        (topbottom_sampler, {'name': 'topbottom', 'priority': 'high'}),
        (random_sampler, {'independent': True})
    ]),
    conditions=conditions
)

# Generate all valid combinations of the steps
valid_combinations = steps.generate_combinations()

# Print out the valid combinations
for combination in valid_combinations:
    print([func.__name__ if func else 'None' for func in combination])
```

### Output

The above script will generate and print the following valid combinations of functions:

```
['tfidf_vectorizer', 'kmeans_clusterer', 'topbottom_sampler']
['tfidf_vectorizer', 'dbscan_clusterer', 'topbottom_sampler']
['count_vectorizer', 'kmeans_clusterer', 'topbottom_sampler']
['count_vectorizer', 'dbscan_clusterer', 'topbottom_sampler']
['None', 'None', 'random_sampler']
```



### Input Structure

- **steps:** A tuple where the first element is the label for the step (e.g., 'vectorizer', 'clusterer', 'sampler'), and the second element is a list of callable objects associated with that step. Each function can optionally be followed by a dictionary of labels.

  These callable objects can include functions, class methods, callable instances, or other similar entities. For example:

  - **Functions**: Standard or lambda functions can be used, such as `[some_function]` or `[lambda x: x * 2]`.
  - **External Library Functions**: Functions or methods from third-party libraries can be included, such as `[vectorizer.fit_transform]`.
  - **Partial Functions**: You can use `functools.partial` to create functions with pre-filled arguments, like `[partial(some_function, multiplier=2)]`.
  - **Class Methods**: Methods from class instances can be used as steps, such as `[my_instance.method]`.
  - **Class Instances with Methods**: You can pass instances of classes where the method is invoked later or the instance itself is callable through a `__call__` method, such as `[KMeansClusterer(num_clusters=100)]`.



- **conditions:** A list of dictionaries defining conditions for valid combinations. Conditions can include:
  - **'require_if_label':** Requires certain steps if a specific label is present on a callable object.
  - **'skip_if_label':** Skips certain steps if a specific label is present on a callable object.
  - **'require_if_present':** Requires certain steps if another step is present.


### Output Structure

The output from the `generate_combinations` method is a list of tuples, where each tuple represents a valid combination of callable objects. Each element in the tuple corresponds to a callable object (or None if a step is skipped) from the respective step in the pipeline.


## Changelog

### [v1.1.0] - 2024-08-18
- Added input validation feature.

### [v1.0.0] - 2024-08-17
- First version.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

