import string


class TeraForm:
    sections = []

    def __init__(self):
        return

    def add_section(self, section):
        self.sections.append(section)

    def to_dict(self):
        sections = []
        for section in self.sections:
            sections.append(section.to_dict())
        return sections


class TeraFormSection:

    def __init__(self, section_id: string, section_label: string):
        self.id = section_id
        self.label = section_label
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def to_dict(self):
        section = {"id": self.id,
                   "label": self.label}
        items = []
        for item in self.items:
            items.append(item.to_dict())
        section["items"] = items
        return section


class TeraFormValue:

    def __init__(self, value_id: string, value: string):
        self.id = value_id
        self.value = value

    def to_dict(self):
        return {"id": self.id, "value": self.value}


class TeraFormItemCondition:

    def __init__(self, condition_item: string,  condition_operator: string, condition_condition: string):
        self.condition = condition_condition
        self.item = condition_item
        self.operator = condition_operator

    def to_dict(self):
        item_condition = {"item": self.item,
                          "op": self.operator,
                          "condition": self.condition}
        return item_condition


class TeraFormItem:

    def __init__(self, item_id: string, item_label: string, item_type: string, item_required: bool = False,
                 item_values: list = None, item_default: string = None, item_condition: TeraFormItemCondition = None):
        self.id = item_id
        self.label = item_label
        self.type = item_type
        self.required = item_required
        self.values = item_values
        self.default = item_default
        self.condition = item_condition

    def set_condition(self, condition: TeraFormItemCondition):
        self.condition = condition

    def to_dict(self):
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

        return item

