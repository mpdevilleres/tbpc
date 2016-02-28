from django.contrib.auth.models import User
from django.db import models
from contract_mgt.models import Contractor
from utils.models import TimeStampedBaseModel, ManytoManyMixin


# Create your models here.


class TeamTask(ManytoManyMixin, TimeStampedBaseModel):
    team_task_no = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    contract_no = models.CharField(max_length=100)
    category = models.PositiveIntegerField(default=0)
    status = models.PositiveIntegerField(default=0)
    severity = models.PositiveIntegerField(default=0)
    end_user = models.CharField(max_length=100)
    remarks = models.TextField(blank=True)
    date_expected = models.DateTimeField(blank=True, null=True)
    date_team_task = models.DateTimeField(blank=True, null=True)
    date_close = models.DateTimeField(blank=True, null=True)
    classification = models.PositiveIntegerField(default=0)
    notify = models.PositiveIntegerField(default=0)

    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    user = models.ManyToManyField(User)

    def __str__(self):
        return "%s" % (self.team_task_no)

    @property
    def choice_alias(self):
        return (self.id, self.team_task_no)

    @property
    def user_names(self):
        return '; '.join([i.username for i in self.user.all()])


class TeamTaskHistory(TimeStampedBaseModel):

    team_task = models.ForeignKey(TeamTask, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # document_id = db.Column(db.Integer,db.ForeignKey('documents.id'))

    action_taken = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    status = models.PositiveIntegerField(default=0)
    date_expected = models.DateTimeField(blank=True, null=True)
    date_action = models.DateTimeField(blank=True, null=True)


# class Document(TimestampMixin,db.Model):
#     __tablename__= 'documents'
#
#     id = db.Column(db.Integer, primary_key=True)
#
#     contractor_id = db.Column(db.Integer, db.ForeignKey('contractors.id'))
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#
#
#     reference_no = db.Column(db.String(60))
#     ref_no_old = db.Column(db.String(60))
#     contract_no = db.Column(db.String(60))
#     counter = db.Column(db.String(5))
#     type_of_doc = db.Column(db.Integer)
#     status = db.Column(db.Integer)
#     subject = db.Column(db.Text)
#     date_document = db.Column(db.DateTime)
#     remarks = db.Column(db.Text)
#     signed_by = db.Column(db.Integer)
#     date_expected = db.Column(db.DateTime)
#     path = db.Column(db.String(255))
#     destination = db.Column(db.Integer)
#     filename = db.Column(db.String(150))
#     technology = db.Column(db.String(60))
#     received_from = db.Column(db.String(60))
#     end_user = db.Column(db.String(255))
#
#     reply_flag =  db.Column(db.Boolean)
#     reserve_flag = db.Column(db.Boolean)
#
#     def __init__(self, contractor_id=None, user_id=None, reference_no=None,
#                  ref_no_old=None, contract_no=None, counter=None,
#                  type_of_doc=None, subject=None, status=None,
#                  date_document=None, remarks=None, signed_by=None,
#                  date_expected=None, path=None, destination=None,
#                  filename=None, technology=None, received_from=None,
#                  end_user=None, reply_flag=False, reserve_flag=False):
#
#         self.contractor_id = contractor_id
#         self.user_id = user_id
#
#         self.reference_no = reference_no
#         self.ref_no_old = ref_no_old
#         self.contract_no = contract_no
#         self.counter = counter
#         self.type_of_doc = type_of_doc
#         self.status = status
#         self.subject = subject
#         self.date_document = date_document
#         self.remarks = remarks
#         self.signed_by = signed_by
#         self.date_expected = date_expected
#         self.path = path
#         self.destination = destination
#         self.filename = filename
#         self.technology = technology
#         self.received_from = received_from
#         self.end_user = end_user
#
#         self.reply_flag = reply_flag
#         self.reserve_flag = reserve_flag
#
#     def gen_counter(self):
#         docs = Document.query.\
#             filter(Document.contractor_id==self.contractor_id).\
#             order_by(Document.id.desc())
#         counter = 0
#
#         if docs.count() > 0:
#             for element in docs:
#                 try:
#                     counter = int(element.counter)
#                     break
#                 except ValueError:
#                     pass
#
#         # try to increment the counter
#         # but if have letter, remove the letter
#         #return int(counter) + 1
#         self.counter = int(counter) + 1
#
#     def gen_ref_no(self):
#         from datetime import datetime as dt
#         contractor = Contractor.query.filter(Contractor.id==self.contractor_id).first()
#         yr = dt.now().year
#         counter = self.counter
#         self.reference_no =  r'ENG.TBPC.{0}.{1}.{2}'.format(contractor.short_hand,
#                                                             yr,
#                                                             str(counter).zfill(4)
#                                                             )
#
#     def get_path(self):
# #    def get_path(vendor_id, dst):
#         import os
#         from project.utils.choices import choices_document_destination
#
#         vendor = Contractor.query.filter(Contractor.id==self.contractor_id).first()
#         vendor_shorthand = vendor.short_hand
#         # CHOICES RETURN TUPLE PAIR, (index, LABEL)
#         #[record.destination-1] since choices starts with index 1, we need to
#         #map it down to 0
#         destination = choices_document_destination()[int(self.destination)-1][1]
#
#         #full_path = os.path.join(app.config['DOC_DIR'], vendor_shorthand,  destination)
#         self.path = os.path.join(vendor_shorthand,  destination)
#
#     def __repr__(self):
#         return '<Document - {}>'.format(self.id)