# -*- coding: utf-8 -*-
import enum
import pycountry


'''
Enum for lang_id, lang_level, lesson_type
'''

LangLevel = enum.Enum("LangLevel", "A1_Beginner "
                                   "A2_Elementary "
                                   "B1_PreIntermediate "
                                   "B2_Intermediate "
                                   "C1_UpperIntermediate "
                                   "C2_Advanced "
                                   "Native ")

LessonType = enum.Enum("LessonType", "ProfessionalLessons "
                                     "InformalTutoring "
                                     "InstantTutoring ")

LangCode = enum.Enum("LangCode", ' '.join([lang.alpha2 for lang in pycountry.languages if hasattr(lang, 'alpha2')]))

