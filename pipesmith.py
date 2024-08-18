# Filename: pipesmith.py
# Copyright (c) 2024 Enrico Altavilla
# Licensed under the MIT License (see LICENSE for details)

class pipesmith:
    __version__ = "1.0.0"

    def __init__(self, *steps, conditions=None):
        """
        Initialize the pipesmith object with steps and conditions.

        Parameters:
        - steps: A tuple containing step labels (e.g., 'vectorizer', 'clusterer', 'sampler')
          and a list of callable objects associated with each step. Each callable object can optionally be followed 
          by a dictionary of labels.
          Example: ('vectorizer', [step1, step2, None]), ...

        - conditions: A list of conditions that define how combinations should be validated.
          Conditions may include:
          - 'require_if_label': Requires certain steps if a label is present on a callable object.
          - 'skip_if_label': Skips certain steps if a label is present on a callable object.
          - 'require_if_present': Requires certain steps if another step is present.

        This method initializes the mapping of step labels to their corresponding indices.
        """
        self.steps = steps
        self.conditions = conditions or []
        self._validate_steps()
        self._validate_conditions()

        self.step_index_map = {label: index for index, (label, _) in enumerate(steps)}



    def _validate_steps(self):
        errors = []

        def validate_step(step):
            if not isinstance(step, tuple) or len(step) != 2:
                errors.append(f"Invalid step format: {step}. Expected a tuple with two elements.")
                return

            label, items = step

            if not isinstance(label, str):
                errors.append(f"Invalid step label: {label}. Expected a string.")

            if not isinstance(items, list):
                errors.append(f"Invalid step items: {items}. Expected a list.")

            for item in items:
                validate_item(item)

        def validate_item(item):
            if item is None:
                return

            if callable(item):
                return

            if isinstance(item, tuple):
                if len(item) != 2:
                    errors.append(f"Invalid item tuple length: {item}. Expected exactly two elements.")
                    return

                func_or_instance, labels = item
                if not callable(func_or_instance) and not isinstance(func_or_instance, object):
                    errors.append(f"Invalid function or instance in tuple: {func_or_instance}. Expected a callable or an object instance.")
                if not isinstance(labels, dict):
                    errors.append(f"Invalid labels in tuple: {labels}. Expected a dictionary.")
            elif not isinstance(item, object):
                errors.append(f"Invalid item: {item}. Expected a callable, an object instance, tuple, or None.")

        for step in self.steps:
            validate_step(step)

        if errors:
            raise ValueError(f"Step validation failed with errors: {errors}")



    def _validate_conditions(self):
        errors = []

        valid_condition_types = {"require_if_label", "skip_if_label", "require_if_present"}
        step_labels = [label for label, _ in self.steps]

        def validate_condition(condition):
            if not isinstance(condition, dict):
                errors.append(f"Invalid condition format: {condition}. Expected a dictionary.")
                return

            condition_type = condition.get("condition")
            if not condition_type or condition_type not in valid_condition_types:
                errors.append(f"Invalid or missing condition type: {condition_type}.")
                return

            target_step = condition.get("target_step")
            if not target_step or not isinstance(target_step, str) or target_step not in step_labels:
                errors.append(f"Invalid or missing target step: {target_step}. Must be one of {step_labels}.")
                return

            if condition_type == "require_if_label" or condition_type == "skip_if_label":
                label = condition.get("label")
                if not label or not isinstance(label, dict):
                    errors.append(f"Invalid or missing label: {label}. Expected a dictionary.")

            if condition_type == "require_if_label":
                required_steps = condition.get("required_steps", [])
                if not isinstance(required_steps, list) or not all(step in step_labels for step in required_steps):
                    errors.append(f"Invalid required steps: {required_steps}. Must be a list of valid step labels.")

            if condition_type == "skip_if_label":
                skip_steps = condition.get("skip_steps", [])
                if not isinstance(skip_steps, list) or not all(step in step_labels for step in skip_steps):
                    errors.append(f"Invalid skip steps: {skip_steps}. Must be a list of valid step labels.")

        for condition in self.conditions:
            validate_condition(condition)

        if errors:
            raise ValueError(f"Condition validation failed with errors: {errors}")



    def get_step_index(self, step_label):
        """
        Retrieve the index of a step by its label.

        Parameters:
        - step_label: The label of the step (e.g., 'vectorizer').

        Returns:
        - The index of the step in the list of steps.
        """
        return self.step_index_map.get(step_label)



    def is_valid_combination(self, current_combination, combination_labels):
        """
        Check if the current combination of steps is valid based on the defined conditions.

        Parameters:
        - current_combination: A list of callable objects currently being combined.
        - combination_labels: A list of dictionaries representing the labels associated with 
          each callable object in the current_combination.

        Returns:
        - True if the combination meets all the conditions, False otherwise.
        """
        for condition in self.conditions:
            if condition["condition"] == "require_if_label":
                # Ensure required steps are present if a specific label is found.
                target_index = self.get_step_index(condition["target_step"])
                target_callable = current_combination[target_index]
                target_labels = combination_labels[target_index]
                if target_callable and condition["label"].items() <= target_labels.items():
                    for step in condition["required_steps"]:
                        required_index = self.get_step_index(step)
                        if current_combination[required_index] is None:
                            return False

            elif condition["condition"] == "skip_if_label":
                # Skip certain steps if a specific label is found.
                target_index = self.get_step_index(condition["target_step"])
                target_callable = current_combination[target_index]
                target_labels = combination_labels[target_index]
                if target_callable and condition["label"].items() <= target_labels.items():
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
        Generate all valid combinations of the steps based on the provided callable objects and conditions.

        Returns:
        - A list of tuples, each tuple representing a valid combination of callable objects.
        """
        combinations = []

        def recursive_generate(current_combination, current_labels, depth):
            """
            Recursive helper function to generate combinations.

            Parameters:
            - current_combination: The current list of callable objects being combined.
            - current_labels: The current list of labels associated with the callable objects.
            - depth: The current depth of recursion, representing the step being processed.
            """
            if depth == len(self.steps):
                if self.is_valid_combination(current_combination, current_labels):
                    combinations.append(tuple(current_combination))
                return
            
            _, callables_with_labels = self.steps[depth]

            for item in callables_with_labels:
                if isinstance(item, tuple) and len(item) == 2:
                    callable_obj, labels = item
                else:
                    callable_obj = item
                    labels = {}
                
                recursive_generate(
                    current_combination + [callable_obj],
                    current_labels + [labels],
                    depth + 1
                )

        recursive_generate([], [], 0)
        return combinations
