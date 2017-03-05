# coding=utf-8

import warnings
import numpy as np
from typing import List, Optional, Tuple, Callable, Dict, Any
from collections import OrderedDict

default_top_level_colors = [
                (0.7, 0.1, 0.1),
                (0.1, 0.1, 0.9),
                (0.1, 0.4, 0.1),
                (0.9, 0.1, 0.9),
                (0.35, 0.25, 0.15),
                (0.15, 0.95, 0.75),
                (0.65, 0.65, 0.05),
                (0.5, 0.05, 0.5),
                (0.9, 0.45, 0.2),
                (0.05, 0.05, 0.3),
                (0.7, 0.6, 0.5),
                (0.95, 0.05, 0.5),
                (0.4, 0.75, 0.95),
                (0.95, 0.95, 0.05),
                (0.05, 0.95, 0.05),
                (0.95, 0.5, 0.5),
                (0.1, 0.5, 0.5),
                (0.7, 0.7, 0.7),
                (1.0, 0.7, 0.85),
                (0.4, 0.05, 0.05),
                (0.7, 1.0, 0.8),
                (0.95, 0.7, 0.0),
                (0.35, 0.0, 0.35),
                (0.4, 0.4, 0.4),
                (1.0, 0.2, 0.3)
               ]

default_cycler = [(0.0, 0.0, 0.0), (0.05, 0.05, 0.0), (-0.05, -0.05, 0.0), (-0.05, 0.05, 0.0), (0.05, -0.05, 0.0),
              (0.05, 0.0, 0.05), (-0.05, 0.0, -0.05), (-0.05, 0.0, 0.05), (0.05, 0.0, -0.05),
              (0.0, 0.05, 0.05), (0.0, -0.05, -0.05), (0.0, -0.05, 0.05), (0.0, 0.05, -0.05),
              (0.04, 0.04, 0.04), (-0.04, -0.04, -0.04),
              (-0.04, -0.04, 0.04), (-0.04, 0.04, -0.04), (0.04, -0.04, -0.04),
              (-0.04, 0.04, 0.04), (0.04, 0.04, -0.04), (0.04, -0.04, 0.04),
              (0.0, 0.0, 0.0), (0.08, 0.0, 0.0), (0.0, 0.08, 0.0), (0.0, 0.0, 0.08),
              (-0.08, 0.0, 0.0), (0.0, -0.08, 0.0), (0.0, 0.0, -0.08)]

class TwoLayerPalette:
    """A color palette that has a number of calc colors and small variations of those colors.
    Useful if you want similar colors for similar things. For example: corgi=teal, terrier=blue; red=cuckoo, orange=finch.
    Example usage:
        import palettable
        top_level_colors = palettable.colorbrewer.qualitative.Set1_9.mpl_colors
        del top_level_colors[5], top_level_colors[-1]  # too light
        palette = TwoLayerPalette(['dog', 'bird'],
                {'dog': ['corgi', 'terrier'], 'bird': ['cuckoo', 'finch']},
                top_level_colors)
        import seaborn as sns
        print(palette.color('bird', 'cuckoo'))
        print(palette.palette_map())
        sns.palplot(palette.palette())
    """

    class_names = None
    top_level_colors = None
    subclass_dict = None
    subclass_difference_coefficient = None
    out_of_bounds_warner = warnings.warn
    
    cycler = default_cycler

    palette_map = None
    
    def __init__(self, class_names: List[str], subclasses_in_class: Dict[str, List[str]],
                 top_level_colors: List[Tuple[float, float, float]]=default_top_level_colors,
                 subclass_difference_coefficient: Callable[[int, str], float]=lambda size, name: 2.0 * np.power(size, 1/5),
                 cycler: Optional[List[Tuple[float, float, float]]]=None,
                 out_of_bounds_warner: Optional[Callable[[str], Any]]=warnings.warn):
        """
        Arguments:
            class_names: The names of the major grouping (e.g. dogs vs birds), where the order matters
                The colors should be apart from each other and away from 0.0 and 1.0 in all three of red, green, and blue.
            subclasses_in_class: A dict mapping each major group to a list of the subclass names, where the order of the list matters
                The values are allowed to overlap for different major groups, but this is not advised.
            top_level_colors: An array of (R, G, B) color tuples where each value is between 0 and 1, inclusive. One element for each class name is required, but can be longer.
            subclass_difference_coefficient: The relative amount of variation from the major colors as a function of the number of subclasses in a class and the class name
                If there are fewer than 26 subclasses in any class, the maximum amount of deviation will be ±0.1*subclass_difference_coefficient in any of red, green, or blue, as well as |red|+|green|+|blue|.
            cycler: The color values to add, starting with (0, 0, 0). The default is probably fine.
            out_of_bounds_warner: If the required variant color extends between the RGB range and needs to be bounded, this function will be called with a warning message.
        """

        if len(class_names) != len(subclasses_in_class):
            raise ValueError("The number of elements in class_names ({}) and subclasses_in_class ({}) must match".format(len(class_names), len(subclasses_in_class)))
        if len(class_names) > len(top_level_colors):
            raise ValueError("There are not enough colors for the classes; {} colors are required but only {} were supplied".format(len(class_names), len(top_level_colors)))

        self.class_names = class_names
        self.subclass_dict = subclasses_in_class
        self.top_level_colors = top_level_colors

        self.subclass_difference_coefficient = subclass_difference_coefficient
        if cycler is not None:
            self.cycler = cycler
            assert len(cycler) > 0
        if out_of_bounds_warner is not None:
            self.out_of_bounds_warner = out_of_bounds_warner

        self.palette_map = self._palette_map()

    def color(self, class_name: str, subclass_name: str):
        return self.palette_map[class_name, subclass_name]

    def _color(self, class_name: str, subclass_name: str) -> Tuple[float, float, float]:
        class_index = self.class_names.index(class_name)
        subclass_index = self.subclass_dict[class_name].index(subclass_name)
        return self._try_color(class_index, subclass_index)

    def palette(self) -> List[Tuple[float, float, float]]:
        return list(self.palette_map.values())
    
    def _palette_map(self) -> Dict[Tuple[str, str], Tuple[float, float, float]]:
        dct = OrderedDict()
        # TODO loop and skip out-of-bounds
        for clazz in self.class_names:
            dct.update({(clazz, subclass): self._color(clazz, subclass) for subclass in self.subclass_dict[clazz]})
        return dct

    def _try_color(self, class_index: int, subclass_index: int):
        class_name = self.class_names[class_index]
        subclass_name = self.subclass_dict[class_name][subclass_index]
        coeff = self.subclass_difference_coefficient(len(self.subclass_dict[class_name]), class_name)
        r = np.array(self.top_level_colors[class_index]) + ((subclass_index+len(self.cycler))//len(self.cycler)) * coeff*np.array(self.cycler[subclass_index % len(self.cycler)])
        t = tuple([self._bound(v, axis, class_name, subclass_name) for v, axis in zip(r, ('red', 'green', 'blue'))])
        return None if None in t else t
    
    def _bound(self, f: float, axis: str, clazz: str, subclass: str) -> Optional[float]:
        if self.out_of_bounds_warner is not None and (f > 1 or f < 0):
            #return None
            self.out_of_bounds_warner("RGB color value {} for {} is not between 0 and 1, inclusive, for class={} and subclass={}".format(f, axis, clazz, subclass))
        return max(min(f, 1.0), 0.0)
