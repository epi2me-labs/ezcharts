"""
Prodict.

MIT License

Copyright (c) 2018 Ramazan Polat (ramazanpolat@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Modified: remove the setting to None of annotated type fields to allow
          better gradual typing of compound structures.
"""

import copy
from typing import Any, List


DICT_RESERVED_KEYS = vars(dict).keys()


def _dict_value(v, is_recursive, exclude_none, exclude_none_in_lists):
    if is_recursive and isinstance(v, Prodict):
        return v.to_dict(is_recursive=is_recursive, exclude_none=exclude_none)
    if exclude_none_in_lists and isinstance(v, List):
        return [
            item.to_dict(exclude_none=True, is_recursive=is_recursive)
            if isinstance(item, Prodict) else item
            for item in v]
    return v


def _none_condition(v, is_recursive, exclude_none):
    if not exclude_none:
        return True
    return False if v is None else True


# noinspection PyMethodParameters
class Prodict(dict):
    """Prodict.

    Dictionary with IDE friendly (auto code completion),
    dot-accessible attributes and more.
    """

    def __init__(self_d921dfa9_4e93_4123_893d_a7e7eb783a32, *args, **kwargs):
        """Initialise the instance.

        https://github.com/ramazanpolat/prodict/issues/15
        """
        super().__init__(*args, **kwargs)

        # MODIFIED: REMOVED THIS SECTION
        # Set all properties to None
        # https://github.com/ramazanpolat/prodict/issues/3

        self_d921dfa9_4e93_4123_893d_a7e7eb783a32.init()
        self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attributes(**kwargs)

    def init(self):
        """Perform any initialisation of object."""
        ...

    def __new__(cls, *args, **kwargs):
        """Create a new object."""
        return super(Prodict, cls).__new__(cls, *args, **kwargs)

    def __getstate__(self):
        """Rehydrate state."""
        return self.to_dict()

    def __setstate__(self, state):
        """Set state."""
        return Prodict.from_dict(state)

    def __deepcopy__(self, memo=None):
        """Deep copy a Prodict."""
        new = self.from_dict({})
        for key in self.keys():
            new.set_attribute(key, copy.deepcopy(self[key], memo=memo))
        return new

    @classmethod
    def from_dict(cls, d: dict):
        """Create a Prodict from a dict."""
        val: cls = cls(**d)
        return val  # type: cls

    @classmethod
    def attr_has_default_value(cls, attr_name):
        """Return True if annotated field has default value."""
        if hasattr(cls, attr_name):
            return True
        return False

    @classmethod
    def get_attr_default_value(cls, attr_name):
        """Return default value of an annotated field."""
        if cls.attr_has_default_value(attr_name):
            return getattr(cls, attr_name)
        else:
            return None

    @classmethod
    def attr_type(cls, attr_name):
        """Type annotation of an attribute."""
        return cls.attr_types()[attr_name]

    @classmethod
    def attr_types(cls):
        """Return set of class annotations."""
        return cls.__annotations__ if hasattr(cls, '__annotations__') else {}

    @classmethod
    def attr_names(cls):
        """Return annotated attribute names."""
        return [k for k, v in cls.attr_types().items()]

    @classmethod
    def has_attr(cls, attr_name):
        """Return True if class has an annotated attribute."""
        return bool(cls.attr_types().get(attr_name))

    def set_default(self, attr_name):
        """Set the default value of and annotated field."""
        if self.attr_has_default_value(attr_name):
            attr_default_type = self.attr_type(attr_name)
            attr_default_value = self.get_attr_default_value(attr_name)
            delattr(self, attr_name)
            self.__annotations__[attr_name] = attr_default_type
            self.set_attribute(attr_name, None)
            self.update({attr_name: attr_default_value})

    def get_constructor(self, attr_name, value):
        """Get required constructor for attribute and value.

        This method is used for type conversion. Prodict uses this method to
        get the type of a value, then based on the value, it return a
        constructor. If the type of a value is 'float' then it returns 'float'
        since 'float' is also a constructor to build a float value.
        """
        attr_type1 = self.attr_type(attr_name)
        constructor = None
        element_type = None
        if attr_type1 == float:
            constructor = float
        elif attr_type1 == str:
            constructor = str
        elif attr_type1 == int:
            constructor = int
        elif attr_type1 == list:
            constructor = list
        elif isinstance(value, Prodict):
            constructor = attr_type1.from_dict
        elif attr_type1 is Any:
            constructor = None
        elif isinstance(value, dict):
            if attr_type1 == dict:
                constructor = Prodict.from_dict
            elif issubclass(attr_type1, Prodict):
                constructor = self.attr_type(attr_name).from_dict
        elif attr_type1 is List:
            # if the type is 'List'
            constructor = list
        elif hasattr(attr_type1, '__origin__'):
            if attr_type1.__dict__['__origin__'] is list:
                # if the type is 'List[something]'
                if len(attr_type1.__args__) == 0:
                    constructor = list
                elif len(attr_type1.__args__) == 1:
                    constructor = List
                    element_type = attr_type1.__args__[0]
                elif len(attr_type1.__args__) > 1:
                    raise TypeError(
                        "Only one dimensional List is supported, like "
                        "List[str], List[int], List[Prodict]")
            elif attr_type1.__dict__['__origin__'] is tuple:
                # if the type is 'Tuple[something]'
                constructor = tuple
        return constructor, element_type

    def set_attribute(self, attr_name, value):
        """Set an attribute to a value."""
        if attr_name in DICT_RESERVED_KEYS:
            raise TypeError("You cannot set a reserved name as attribute")
        if self.has_attr(attr_name):
            if value is None:
                self.update({attr_name: None})
            elif self.attr_type(attr_name) == Any:
                self[attr_name] = value
            else:
                constructor, element_type = self.get_constructor(
                    attr_name, value)
                if constructor is None:
                    self.update({attr_name: value})
                elif constructor == List:
                    value_list: List[element_type] = value
                    new_list: List[element_type] = []

                    if issubclass(element_type, Prodict):
                        element_constructor = element_type.from_dict
                    else:
                        element_constructor = element_type

                    for v in value_list:
                        new_list.append(element_constructor(v))
                    self.update({attr_name: new_list})
                elif constructor == list:
                    self.update({attr_name: list(value)})
                else:
                    self.update({attr_name: constructor(value)})
        else:
            if isinstance(value, dict):
                if isinstance(value, Prodict):
                    constructor = value.from_dict
                else:
                    constructor = Prodict.from_dict
                self.update({attr_name: constructor(value)})
            else:
                self.update({attr_name: value})

    def set_attributes(self_d921dfa9_4e93_4123_893d_a7e7eb783a32, **d):
        """
        Set a set of attributes.

        https://github.com/ramazanpolat/prodict/issues/15
        """
        for k, v in d.items():
            self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attribute(k, v)

    def __getattr__(self, item):
        """Get attribute."""
        return self[item]

    def __setattr__(self, name: str, value):
        """Set attribute."""
        self.set_attribute(name, value)

    def to_dict(
            self, *args,
            is_recursive=False, exclude_none=False,
            exclude_none_in_lists=False, **kwargs):
        """Return a nice dictionary."""
        ret = {
            k: _dict_value(
                v, is_recursive=is_recursive,
                exclude_none=exclude_none,
                exclude_none_in_lists=exclude_none_in_lists)
            for k, v in self.items()
            if _none_condition(
                v, is_recursive=is_recursive, exclude_none=exclude_none)}

        return ret