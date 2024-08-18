# Filename: pipesmith.py
# Copyright (c) 2024 Enrico Altavilla
# Licensed under the MIT License (see LICENSE for details)

class pipesmith:
    __version__ = "1.0.0"
    def __init__(self, *function_steps, conditions=None):
        """
        Initialize the pipesmith object with steps and conditions.

        Parameters:
        - function_steps: A tuple containing step labels (e.g., 'vectorizer', 'clusterer', 'sampler')
          and a list of functions associated with each step. Each function can optionally be followed 
          by a dictionary of labels.
          Example: ('vectorizer', [func1, func2, None]), ...

        - conditions: A list of conditions that define how combinations should be validated.
          Conditions may include:
          - 'require_if_label': Requires certain steps if a label is present on a function.
          - 'skip_if_label': Skips certain steps if a label is present on a function.
          - 'require_if_present': Requires certain steps if another step is present.

        This method initializes the mapping of step labels to their corresponding indices.
        """
        self.function_steps = function_steps
        self.conditions = conditions or []
        self.step_index_map = {label: index for index, (label, _) in enumerate(function_steps)}

    def get_step_index(self, step_label):
        """
        Retrieve the index of a step by its label.

        Parameters:
        - step_label: The label of the step (e.g., 'vectorizer').

        Returns:
        - The index of the step in the list of function_steps.
        """
        return self.step_index_map.get(step_label)

    def is_valid_combination(self, current_combination, combination_labels):
        """
        Check if the current combination of steps is valid based on the defined conditions.

        Parameters:
        - current_combination: A list of functions currently being combined.
        - combination_labels: A list of dictionaries representing the labels associated with 
          each function in the current_combination.

        Returns:
        - True if the combination meets all the conditions, False otherwise.
        """
        for condition in self.conditions:
            if condition["condition"] == "require_if_label":
                # Ensure required steps are present if a specific label is found.
                target_index = self.get_step_index(condition["target_step"])
                target_function = current_combination[target_index]
                target_labels = combination_labels[target_index]
                if target_function and condition["label"].items() <= target_labels.items():
                    for step in condition["required_steps"]:
                        required_index = self.get_step_index(step)
                        if current_combination[required_index] is None:
                            return False

            elif condition["condition"] == "skip_if_label":
                # Skip certain steps if a specific label is found.
                target_index = self.get_step_index(condition["target_step"])
                target_function = current_combination[target_index]
                target_labels = combination_labels[target_index]
                if target_function and condition["label"].items() <= target_labels.items():
                    for step in condition["skip_steps"]:
                        skip_index = self.get_step_index(step)
                        if current_combination[skip_index] is not None:
                            return False

            elif condition["condition"] == "require_if_present":
                # Ensure certain steps are present if another step is present.
                target_index = self.get_step_index(condition["target_step"])
                if current_combination[target_index] is not None:
                    for step in condition["required_steps"]:
                        required_index = self.get_step_index(step)
                        if current_combination[required_index] is None:
                            return False

        return True

    def generate_combinations(self):
        """
        Generate all valid combinations of the steps based on the provided functions and conditions.

        Returns:
        - A list of tuples, each tuple representing a valid combination of functions.
        """
        combinations = []

        def recursive_generate(current_combination, current_labels, depth):
            """
            Recursive helper function to generate combinations.

            Parameters:
            - current_combination: The current list of functions being combined.
            - current_labels: The current list of labels associated with the functions.
            - depth: The current depth of recursion, representing the step being processed.
            """
            if depth == len(self.function_steps):
                if self.is_valid_combination(current_combination, current_labels):
                    combinations.append(tuple(current_combination))
                return
            
            _, funcs_with_labels = self.function_steps[depth]

            for item in funcs_with_labels:
                if isinstance(item, tuple) and len(item) == 2:
                    func, labels = item
                else:
                    func = item
                    labels = {}
                
                recursive_generate(
                    current_combination + [func],
                    current_labels + [labels],
                    depth + 1
                )

        recursive_generate([], [], 0)
        return combinations
