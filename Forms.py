from flask_wtf import FlaskForm
from wtforms import StringField, DateField,TextAreaField,FileField,validators
from wtforms.validators import DataRequired

class leaveForm(FlaskForm):
    staff_id = StringField('Staff ID', render_kw={'readonly': True})
    starting_date = DateField('Starting Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    reason = StringField('Reason', validators=[DataRequired()])

class mcForm(FlaskForm):
    staff_id = StringField('Staff ID', render_kw={'readonly': True})
    starting_date = DateField('Starting Date of SOA', [validators.DataRequired()], format='%Y-%m-%d')
    end_date = DateField('Ending Date of SOA', [validators.DataRequired()], format='%Y-%m-%d')
    proof=FileField("Supporting Document",[validators.DataRequired()])
