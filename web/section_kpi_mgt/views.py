from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.generic import View

from section_kpi_mgt.forms import AddSpecForm, AddKPIForm
from section_kpi_mgt.tables_ajax import SpecJson
from utils.forms import populate_obj
from utils.kpi_calculator import KpiCalculator
from section_kpi_mgt.models import SpecSectionKpi, SectionRawScore, SectionWeightedScore
from utils.decorators import team_decorators, section_decorators

import datetime as dt
import pandas as pd

@method_decorator(team_decorators, name='dispatch')
class AddSpecView(View):
    model = SpecSectionKpi
    form_class = AddSpecForm
    template_name = 'default/add_form.html'
    success_redirect_link = 'section_kpi_mgt:table_specification'

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        if pk is None:
            forms = self.form_class()

        else:
            record = get_object_or_404(self.model, pk=pk)
            forms = self.form_class(initial=record.__dict__)

        return render(request, self.template_name, {'forms': forms})

    def post(self, request, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        if pk is None:
            record = self.model()
        else:
            record = get_object_or_404(self.model, pk=pk)

        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            cleaned_data = form.clean()
            populate_obj(cleaned_data, record)
            spec_date = cleaned_data['spec_date']
            record.filename = spec_date.strftime('%Y-%b.xlsx')
            record.data = {}
            record.save()

            kpi_calc = KpiCalculator(kpi_file=record.file.path)
            kpi_calc.kpi_xl_to_spec()
            record.data = kpi_calc._all_specs
            record.save()

            messages.success(request, "Successfully Updated the Database")
            return redirect(self.success_redirect_link)

        return render(request, self.template_name, {'forms': form})


@method_decorator(team_decorators, name='dispatch')
class AddKpiView(View):
    model = SectionRawScore
    form_class = AddKPIForm
    template_name = 'default/add_form.html'
    success_redirect_link = 'section_kpi_mgt:table_specification'
    _func_name = 'section_kpi_mgt:add_kpi'

    coming_soon_template = 'section_kpi_mgt/coming-soon.html'

    def get(self, request, *args, **kwargs):
        year = kwargs.pop('year', None)
        month = kwargs.pop('month', None)
        section_id = kwargs.pop('section_id', None)

        filename = '%s-%s' % (year, month)

        if (year and month) is None or section_id is None:
            raise Http404()

        specs = SpecSectionKpi.objects.filter(spec_date__year__gte=year,
                                              spec_date__year__lte=year,
                                              spec_date__month__gte=month,
                                              spec_date__month__lte=month,
                                              ).first()

        section_name = User.objects.filter(pk=section_id).first().first_name

        if specs is None:
            context = {
                'msg': "Record for {} doesn't exist yet".format(filename)
            }
            return render(request, self.coming_soon_template, context)

        try:
            description = specs.data[section_name]['_classes_description']
        except KeyError:
            context = {
                'msg': "Specification for {}:{} doesn't exist yet".format(section_name, filename)
            }
            return render(request, self.template_name, context)

        # getting initial Values
        records = SectionRawScore.objects.filter(score_date__year__gte=year,
                                              score_date__year__lte=year,
                                              score_date__month__gte=month,
                                              score_date__month__lte=month,
                                              section_id=section_id
                                              ).all()
        if len(records) != 0:
            initial = {}
            for record in records:
                initial[record.score_class] = record.raw_score
        else:
            initial = {}

        form = self.form_class(description=description, initial=initial)

        context ={
            'forms': form
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        year = kwargs.pop('year', None)
        month = kwargs.pop('month', None)
        section_id = kwargs.pop('section_id', None)

        records = SectionRawScore.objects.filter(score_date__year__gte=year,
                                              score_date__year__lte=year,
                                              score_date__month__gte=month,
                                              score_date__month__lte=month,
                                              section_id=section_id
                                              ).all()

        # Deletes records if exist to create an illusion of edit
        if len(records) != 0:
            for record in records:
                record.delete()

        specs = SpecSectionKpi.objects.filter(spec_date__year__gte=year,
                                              spec_date__year__lte=year,
                                              spec_date__month__gte=month,
                                              spec_date__month__lte=month,
                                              ).first()

        section_name = User.objects.filter(pk=section_id).first().first_name
        description = specs.data[section_name]['_classes_description']
        form = self.form_class(request.POST, description=description)

        if form.is_valid():
            cleaned_data = form.clean()
            for key, value in cleaned_data.items():
                record = self.model(section_id=section_id,
                                    score_date=dt.datetime(year=int(year),month=int(month),day=1),
                                    score_class=key,
                                    raw_score=value)
                record.save()

            # Calculate Raw Score
            kpi_calculator = KpiCalculator(raw_score=cleaned_data)
            kpi_calculator.set_spec(specs.data[section_name])
            kpi_calculator.run()
            records = SectionWeightedScore.objects.filter(section_id=section_id,
                                                        weighted_score_date__year__gte=year,
                                                        weighted_score_date__year__lte=year,
                                                        weighted_score_date__month__gte=month,
                                                        weighted_score_date__month__lte=month,
                                                         ).all()
            if len(records) != 0:
                for record in records:
                    record.delete()

            for k, v in kpi_calculator._weighted_category_scores.items():
                record = SectionWeightedScore(
                    section_id=section_id,
                    weighted_score_date=dt.datetime(year=int(year),month=int(month),day=1),
                    weighted_score=v,
                    category=k
                )
                record.save()

            messages.success(request, "Successfully Updated the Database")
            return redirect(self.success_redirect_link)

        context = {
            'forms': form
        }

        return render(request, self.template_name, context)

@method_decorator(team_decorators, name='dispatch')
class SelectAddKpiView(View):
    model = None
    form_class = None
    template_name = 'section_kpi_mgt/select-add-kpi.html'


    def get(self, request, *args, **kwargs):
        parameter = kwargs.pop('parameter', None)
        if parameter is None:
            sections = User.objects.filter(employee__section=True).all()
            data = []
            for section in sections:
                data.append(
                    (section.id, section.first_name)
                )
            _section_name = None

            url = 'section_kpi_mgt:select_add_kpi'

        else:
            data = []
            for month_n in range(1,13): # range is 1 - 12
                date = '{} 2016'.format(dt.datetime(1900, month_n, 1).strftime('%B'))
                data.append(
                    (r'2016/%02d/%s' % (month_n, parameter),
                     date)
                )
            _section_name = User.objects.filter(pk=parameter).first().first_name

            url = 'section_kpi_mgt:add_kpi'

        context = {
            'section_name' : _section_name,
            'data' : data,
            'url' : reverse_lazy(url)
        }

        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
       raise Http404()

# Tables
@method_decorator(team_decorators, name='dispatch')
class TableSpecView(View):
    add_record_link = reverse_lazy('section_kpi_mgt:add_specification')
    columns = getattr(SpecJson,'column_names')
    data_table_url = reverse_lazy('section_kpi_mgt:table_specification_json')
    template_name = 'default/datatable.html'
    table_title = 'KPI Specification'

    def get(self, request, *args, **kwargs):

        pk = kwargs.pop('pk', None)
        if pk is not None:
            self.data_table_url = self.data_table_url + pk

        context = {
            'table_title': self.table_title,
            'columns': self.columns,
            'data_table_url': self.data_table_url,
            'add_record_link': self.add_record_link,
        }
        return render(request, self.template_name, context)


@method_decorator(team_decorators, name='dispatch')
class DashboardKpiAllView(View):
    model = None
    form_class = None
    template_name = 'section_kpi_mgt/dashboard-overall.html'

    def get(self, request, *args, **kwargs):
        df_kpi = pd.DataFrame.from_records(SectionWeightedScore.objects.values())
        df_section = pd.DataFrame.from_records(User.objects.filter(employee__section=True).values())
        merged = pd.merge(df_kpi, df_section, left_on='section_id', right_on='id', how='left')
        merged['date-grouping'] = merged['weighted_score_date'].\
                apply(lambda x : x.strftime('%Y-%m'))
        merged = merged[[u'weighted_score_date', u'weighted_score', u'category',u'first_name', u'date-grouping']]
        merged = merged.rename(
            columns={
                'first_name': 'section'
            }
        )
        gp = merged.groupby('date-grouping')
        groupings = sorted(list(gp.groups.keys()))
        gp_section = gp.get_group(groupings[-1])
        pivoted = gp_section.pivot(index='section', columns='category', values='weighted_score').reset_index()

        #index   date-grouping  section     category                weighted_score
        #0       2016-01        MAM         initiativescapexopex    47.13
        grouped = merged.groupby(['date-grouping','section']).sum().reset_index()

        # convert "weighted_score" object type to float type
        grouped['weighted_score'] = grouped['weighted_score'].astype('float')

        all_month = grouped.groupby('date-grouping').mean().reset_index().to_json(orient='records')

        data = pivoted.to_json(orient='records')

        context = {
            'all_month': all_month,
             'data': data
        }

        return render(request, self.template_name, context)

@method_decorator(section_decorators, name='dispatch')
class DashboardKpiView(View):
    model = None
    form_class = None
    template_name = 'section_kpi_mgt/dashboard.html'
    coming_soon_template = 'section_kpi_mgt/coming-soon.html'

    def get(self, request, *args, **kwargs):
#        section_id = request.user.id
        section_id = 1007
        today = dt.datetime.now()

        record = SectionWeightedScore.objects.filter(section_id=section_id).all()

        if len(record) == 0:
            return render(request, self.coming_soon_template)

        df_kpi = pd.DataFrame.from_records(record.values())
        df_kpi = df_kpi.set_index('category')
        df_kpi['date-grouping'] = df_kpi['weighted_score_date'].\
            apply(lambda x : x.strftime('%Y-%m'))
        df_kpi['date-year'] = df_kpi['weighted_score_date'].\
            apply(lambda x : x.strftime('%Y'))

        df_kpi_grouped = df_kpi.groupby('date-grouping')

        date_groups = list(df_kpi_grouped.groups.keys())

        lastest_mn = df_kpi_grouped.get_group(date_groups[-1])
        # To Solve Error When there's no previous month data
        try:
            prev_kpi = df_kpi_grouped.get_group(date_groups[-2])
        except IndexError:
            prev_kpi = lastest_mn

        # for getting by year data
        data_list = []
        keys = list(df_kpi_grouped.groups.keys())
        for key in sorted(keys):
            temp_df = df_kpi_grouped.get_group(key)
            data_list.append(
                {
                    'year-mn': key,
                    'capex' : float(temp_df.loc['capex','weighted_score']),
                    'opex' : float(temp_df.loc['opex','weighted_score']),
                    'initiatives' : float(temp_df.loc['initiatives','weighted_score'])
                }
            )

        by_month = {
            'previous': prev_kpi['weighted_score'].sum(),
            'current': lastest_mn['weighted_score'].sum(),
            'arrow': 'up' if lastest_mn['weighted_score'].sum() > prev_kpi['weighted_score'].sum() else 'down',

            'opex': lastest_mn['weighted_score']['opex'],
            'o_sign': '+' if lastest_mn['weighted_score'].sum() > prev_kpi['weighted_score'].sum() else '-',

            'capex': lastest_mn['weighted_score']['capex'],
            'c_sign': '+' if lastest_mn['weighted_score'].sum() > prev_kpi['weighted_score'].sum() else '-',

            'initiatives' : lastest_mn['weighted_score']['initiatives'],
            'i_sign': '+' if lastest_mn['weighted_score'].sum() > prev_kpi['weighted_score'].sum() else '-'
        }
        by_year = {
            'previous': df_kpi[df_kpi['date-year']=='%s' % (today.year - 1)]['weighted_score'].mean(),
            'current': df_kpi[df_kpi['date-year']==today.strftime('%Y')]['weighted_score'].mean(),
            'data_provider': data_list,
            'arrow': 'down' \
                if df_kpi[df_kpi['date-year']==today.strftime('%Y')]['weighted_score'].mean() < \
                   df_kpi[df_kpi['date-year']=='%s' % (today.year - 1)]['weighted_score'].mean()
                else 'up'
        }


        context = {
            'by_month': by_month,
            'by_year': by_year
        }

        return render(request, self.template_name, context)

@method_decorator(section_decorators, name='dispatch')
class ReviewKpiView(View):
    model = None
    form_class = None
    template_name = 'section_kpi_mgt/detailed-dashboard.html'
    template_coming_soon = 'section_kpi_mgt/coming-soon.html'

    def get(self, request, *args, **kwargs):
        '''
        Review Details of the KPI per section by month and year
        '''

        year = kwargs.pop('year', None)
        month = kwargs.pop('month', None)

        section_id = request.user.id
        section = User.objects.filter(pk=section_id).first()

        if section is None:
            raise Http404()

        specs = SpecSectionKpi.objects.filter(spec_date__year__gte=year,
                                              spec_date__year__lte=year,
                                              spec_date__month__gte=month,
                                              spec_date__month__lte=month,
                                              ).first()
        if specs is None:
            context = {
                'msg': "Specification for {}-{} doesn't exist yet".format(year, month)
            }
            return render(self.template_coming_soon, context)

        spec = specs.data[section.first_name]
        classes_description = spec['_classes_description']
        targets = spec['_target']
        data={}

        records = SectionRawScore.objects.filter(score_date__year__gte=year,
                                                score_date__year__lte=year,
                                                score_date__month__gte=month,
                                                score_date__month__lte=month,
                                                section_id=section_id
                                                ).all()

        if len(records) == 0:
            context = {
                'msg': "Raw Score doesn't exist yet"
            }
            return render(self.template_coming_soon, context)

        df = pd.DataFrame.from_records(records.values())
        df = df.set_index('score_class')

        temp_list = []
        for i in ['a11','a12','a13','a2','a3']:
            temp_list.append(
                {
                    "class": classes_description[i],
                    "target": targets[i],
                    "actual": float(df.loc[i,'raw_score'])
                }
            )
        data['capex'] = temp_list

        temp_list = []
        for i in ['b1','b2']:
            temp_list.append(
                {
                    "class": classes_description[i],
                    "target": targets[i],
                    "actual": float(df.loc[i,'raw_score'])
                }
            )
        data['opex'] = temp_list

        temp_list = []
        for i in ['c1','c2']:
            temp_list.append(
                {
                    "class": classes_description[i],
                    "target": targets[i],
                    "actual": float(df.loc[i,'raw_score'])
                }
            )
        data['initiatives'] = temp_list

        context = {
            'data':data

        }
        return render(request, self.template_name, context)