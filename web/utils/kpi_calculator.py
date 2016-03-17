##########################
## KPI CALCULATOR CLASS ##
##########################

# Imports
import pandas as pd
from decimal import Decimal


class KpiCalculator(object):

    # Variables
    _classes = list()
    _classes_description = dict()
    _criteria = dict()
    _weightage_category = dict()
    _weightage_class = dict()
    _target = dict()
    _categories = {
        'capex': 'a',
        'opex': 'b',
        'initiatives': 'c'
    }

    _all_specs = dict()
    # Computed Values
    _equivalent_scores = dict()
    _weighted_class_scores = dict()
    _weighted_category_scores = dict()

    def __init__(self, *args, **kwargs):
        # Temp Vars
        self._kpi_file = kwargs.pop('kpi_file', None)
        self._section = kwargs.pop('section', None)
        self._raw_score = kwargs.pop('raw_score', None)

    def kpi_xl_to_spec(self):
        xl = pd.ExcelFile(self._kpi_file)
        for section in xl.sheet_names:
            _classes = list()
            _classes_description = dict()
            _criteria = dict()
            _weightage_category = dict()
            _weightage_class = dict()
            _target = dict()
            _actual = dict()
            df = xl.parse(section)
            df_spec = df[['serial_no','Key Objectives','Weightage','Target Monthly','Points','Criteria']]
            df_overall = df[['Focus Area', 'Overall Weightage']]
            # group per class
            df_spec_grouped = df_spec.groupby('serial_no')
            for group in df_spec_grouped:
                # Create a List of Classes
                group_name = group[0]
                _classes.append(group_name)
                # Gets the dataframe of a group
                data = group[1]
                # Iterate all allrows in the a group dataframe
                # and create a from score_eq(point, low, high)
                # Temp List
                temp_point_equivalent = list()
                for index in data.index:
                    criteria = data.loc[index, 'Criteria']
                    point = data.loc[index, 'Points']
                    low, high = criteria.split(' - ')
                    temp_point_equivalent.append(
                        (point, int(low), int(high))
                    )
                # Store the list of points in a Class Dictionary
                _criteria[group_name] = temp_point_equivalent

                # Store Other Specs
                # data.index[0] ensure to get the first row in the dataframe
                _classes_description[group_name] = data.get_value(data.index[0],'Key Objectives')
                _weightage_class[group_name] = data.get_value(data.index[0],'Weightage')
                _target[group_name] = data.get_value(data.index[0],'Target Monthly')
                _actual[group_name] = data.get_value(data.index[0],'Actual')

                # Get Weightage per Category
                df_overall = df_overall.dropna()
                df_overall['new_index']=df_overall['Focus Area'].apply(lambda x: x.lower())
                df_overall = df_overall.set_index('new_index')
                for k,v in self._categories.items():
                    _weightage_category[k] = df_overall.get_value(k,'Overall Weightage')

            self._all_specs[section] ={
                '_classes' : _classes,
                '_classes_description' : _classes_description,
                '_criteria' : _criteria,
                '_weightage_category' : _weightage_category,
                '_weightage_class' : _weightage_class,
                '_target' : _target,
                '_actual': _actual,
                '_categories' : self._categories
                }

    def set_spec(self, spec_dict=None):
        for k, v in spec_dict.items():
            setattr(self, k, v)

    def cal_score_equivalent(self):
        '''
        score = raw_score/target_score * 100
        Then
        Gets the score equivalent depending on the criteria set per class
        INPUT
        {
            'a11' : 9,
            ....
            'c2' : 78
        }
        OUTPUT
        '''
        eq_scores = {}

        if self._raw_score is None:
            self._raw_score = {}

        for key, raw in self._raw_score.items():
            #eq_scores[key] = 0

            score = (float(raw)/self._target[key])*100
            for equivalent, low, high in self._criteria[key]:
                if low <= score < high:
                    eq_scores[key] = equivalent
                    break
                # if the score is equal to the last maximum value in the criteria
#                elif (equivalent, low, high)== self._criteria[key][-1] and score==high:
                else:
                    eq_scores[key] = equivalent

        self._equivalent_scores = eq_scores

    def cal_weighted_each_class(self):
        weighted_score = {}
        for i in self._classes:
            weighted_score[i] = self._equivalent_scores[i] * self._weightage_class[i]
        self._weighted_class_scores = weighted_score

    def cal_weighted_each_category(self):

        weighted_category_scores = {}
        # """
        # score structure
        # {
        #     'a11' : 100,
        #     'a12': 100,
        #     ...
        #     'a13' : 100,
        # }
        # """
        df = pd.DataFrame(list(self._weighted_class_scores.items()),
                          columns=['classes', 'weighted_score'])
        # """
        # Dataframe Structure
        #    classes  weighted_score
        # 0      a13            1.00
        # 1       c1            6.25
        # 2       a3            9.00
        # 3       a2            6.25
        # """
        df['categories'] = df['classes'].apply(lambda x: x[0])
        # """
        #    classes  weighted_score categories
        # 0      a13            1.00          a
        # 1       c1            6.25          c
        # 2       a3            9.00          a
        # 3       a2            6.25          a
        # """
        df = df.groupby('categories').sum()
        df_dict = df.to_dict()
        # """
        # {'weighted_score': {'a': 31.5, 'b': 17.25, 'c': 15.25}}
        # """
        total_score_each_category = df_dict['weighted_score']
        for k, v in self._categories.items():
            weighted_category_scores[k] = total_score_each_category[v] * (self._weightage_category[k])
        self._weighted_category_scores = weighted_category_scores

    def run(self):
        self.cal_score_equivalent()
        self.cal_weighted_each_class()
        self.cal_weighted_each_category()

    @property
    def spec(self):
        return {'classes' : self._classes,
                'classes_description' : self._classes_description,
                'criteria' : self._criteria,
                'weightage_category' : self._weightage_category,
                'weightage_class' : self._weightage_class,
                'target' : self._target,
                'categories' : self._categories
                }

    @property
    def equivalent_score(self):
        try:
            return self._equivalent_scores
        except NameError:
            Exception('Equivalent Score Did not compute')

    @property
    def weightage_class_scores(self):
        try:
            return self._weighted_class_scores
        except NameError:
            Exception('Weighted Class Score Did not compute')

    @property
    def weighted_category_scores(self):
        try:
            return self._weighted_category_scores
        except NameError:
            Exception('Weighted Category Score Did not compute')