# pipesmith

**pipesmith** is a Python utility class designed to help you create and validate pipelines by combining different functions or steps, each potentially labeled with metadata. This tool is particularly useful for constructing machine learning pipelines or any other process that involves multiple sequential steps, where specific conditions must be met.

## Features

- **Flexible Pipeline Construction:** Combine different functions into valid pipelines based on custom conditions.
- **Label-Based Validation:** Apply conditions to ensure certain steps are included, excluded, or required based on the labels associated with the functions.
- **Simple Integration:** Easily integrate `pipesmith` into any Python project requiring dynamic pipeline creation.

## Usage

### Basic Example

Here’s a basic example of how to use the `pipesmith` class to create and validate function combinations.

```python
from pipesmith import pipesmith

# Define some example functions
def tfidf_vectorizer(): pass
def count_vectorizer(): pass
def kmeans_clusterer(): pass
def dbscan_clusterer(): pass
def top_sampler(): pass
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
        "label": {"name": "top"},
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
        (top_sampler, {'name': 'top', 'type': 'sampler', 'priority': 'high'}),
        (random_sampler, {'independent': True, 'name': 'random', 'type': 'sampler'})
    ]),
    conditions=conditions
)

# Generate all valid combinations of the steps
valid_combinations = steps.generate_combinations()

# Print out the valid combinations
for combination in valid_combinations:
    print([func.__name__ if func else 'None' for func in combination])
```

### Input Structure

- **function_steps:** A tuple where the first element is the label for the step (e.g., 'vectorizer', 'clusterer', 'sampler'), and the second element is a list of functions associated with that step. Each function can optionally be followed by a dictionary of labels.
  
  Example:
  ```python
  ('vectorizer', [
      tfidf_vectorizer,  # No labels
      count_vectorizer,  # No labels
      None  # Optional None to indicate no vectorizer
  ])
  ```

- **conditions:** A list of dictionaries defining conditions for valid combinations. Conditions can include:
  - **'require_if_label':** Requires certain steps if a specific label is present on a function.
  - **'skip_if_label':** Skips certain steps if a specific label is present on a function.
  - **'require_if_present':** Requires certain steps if another step is present.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss changes.
