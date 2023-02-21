import string


class TeraForm:
    def __init__(self, object_name):
        self.sections = []
        self.object_name = object_name

    def add_section(self, section):
        self.sections.append(section)

    def to_dict(self):
        sections = []
        order = 1
        for section in self.sections:
            sections.append(section.to_dict(order))
            order += 1
        object_dict = {'objecttype': self.object_name,
                       'sections': sections}
        return object_dict


class TeraFormSection:

    def __init__(self, section_id: string, section_label: string):
        self.id = section_id
        self.label = section_label
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def to_dict(self, order: int = -1):
        section = {"id": self.id,
                   "label": self.label}

        if order >= 0:
            section['_order'] = order
        items = []
        item_order = 1
        for item in self.items:
            items.append(item.to_dict(item_order))
            item_order += 1
        section["items"] = items
        return section


class TeraFormItemCondition:

    # condition_item = any item in the form
    # condition_operator = operator of the form "=", "<>", ">" ...
    # condition_condition = value to check. Special flags: "changed"
    # hook = api call to get new values for that item when condition is true
    def __init__(self, condition_item: str,  condition_operator: str, condition_condition, hook: str = None):
        self.condition = condition_condition
        self.item = condition_item
        self.operator = condition_operator
        self.hook = hook

    def to_dict(self):
        item_condition = {"item": self.item,
                          "op": self.operator,
                          "condition": self.condition}
        if self.hook:
            item_condition["hook"] = self.hook
        return item_condition


class TeraFormValue:

    def __init__(self, value_id: string, value: string):
        self.id = value_id
        self.value = value

    def to_dict(self):
        base_dict = {"id": self.id, "value": self.value}
        return base_dict


class TeraFormItem:

    def __init__(self, item_id: str, item_label: str, item_type: str, item_required: bool = False,
                 item_values: list | None = None, item_default: str | None | bool = None,
                 item_condition: TeraFormItemCondition | None = None, item_options=None):
        if item_options is None:
            item_options = {}
        self.id = item_id
        self.label = item_label
        self.type = item_type
        self.required = item_required
        self.values = item_values
        self.default = item_default
        self.condition = item_condition
        self.options = item_options

    def set_condition(self, condition: TeraFormItemCondition):
        self.condition = condition

    def to_dict(self, order: int = -1):
        item = {"id": self.id,
                "label": self.label,
                "type": self.type,
                }
        if self.required:
            item["required"] = True

        if self.values:
            values = []
            id_index = 0
            for value in self.values:
                if isinstance(value, TeraFormValue):
                    values.append(value.to_dict())
                elif isinstance(values, list):
                    values.append(TeraFormValue(str(id_index), value).to_dict())
                    id_index += 1

            item["values"] = values

        if self.default:
            item["default"] = self.default

        if self.condition:
            item["condition"] = self.condition.to_dict()

        if order >= 0:
            item['_order'] = order

        if len(self.options) > 0:
            for option in self.options:
                item[option] = self.options[option]

        return item
