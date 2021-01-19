import datetime

from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource, abort
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, ValidationError, validate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Pupils.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)


def validate_date(birth_date):
    day, month, year = birth_date.split('-')
    birth_date = datetime.date(int(year), int(month), int(day))
    today = datetime.date.today()
    y = today.year - birth_date.year
    if 5 <= y < 20:
        return birth_date
    else:
        abort(404, message="Your age can not be more than 20 or less than 5.")


class Pupil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date(), nullable=False)
    school_class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'),
                                nullable=True)
    school_class = db.relationship('SchoolClass',
                                   backref=db.backref('pupils', lazy=True))

    def __repr__(self):
        return "(%s, %s, %s)" % (self.first_name, self.last_name, self.school_class)


class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "(%s, %s)" % (self.name, self.course)


class SchoolClassSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "course")


class PupilSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=2))
    last_name = fields.Str(required=True, validate=validate.Length(min=2))
    birth_date = fields.Date(required=True)
    school_class = fields.Nested(SchoolClassSchema)

    class Meta:
        dateformat = '%d-%m-%Y'


pupil_schema = PupilSchema()
school_class_schema = SchoolClassSchema()
pupils_schema = PupilSchema(many=True)
school_classes_schema = SchoolClassSchema(many=True)


class PupilListResource(Resource):
    def get(self):
        pupils = Pupil.query.order_by('last_name').all()
        # r = db.session.query(Pupil).join(SchoolClass, Pupil.school_class_id == SchoolClass.id).group_by(
        #     Pupil.school_class_id).order_by('last_name').all()
        pupils = db.session.query(Pupil).group_by(Pupil.school_class_id, Pupil.last_name).order_by(Pupil.school_class_id, Pupil.last_name).all()
        if not pupils:
            abort(404, message="There are no pupils exists.")
        return pupils_schema.dump(pupils)

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400
        try:
            data = pupil_schema.load(json_data)
        except ValidationError as err:
            return err.messages, 422
        birth_date = validate_date(request.json['birth_date'])
        new_pupil = Pupil(
            first_name=request.json['first_name'],
            last_name=request.json['last_name'],
            birth_date=birth_date
        )
        db.session.add(new_pupil)
        db.session.commit()
        return {"message": "Created new pupil.", "pupil": pupil_schema.dump(new_pupil)}, 201


class SchoolClassListResource(Resource):
    def get(self):
        school_class = SchoolClass.query.all()
        return school_classes_schema.dump(school_class)


class PupilSingleResource(Resource):
    def get(self, pupil_id):
        pupil_obj = Pupil.query.get_or_404(pupil_id, description=f"Pupil with id {pupil_id} not found.")
        return pupil_schema.dump(pupil_obj)

    def patch(self, pupil_id):
        pupil_obj = Pupil.query.get_or_404(pupil_id, description=f"Pupil with id {pupil_id} not found.")

        if 'first_name' in request.json:
            pupil_obj.first_name = request.json['first_name']
        if 'last_name' in request.json:
            pupil_obj.last_name = request.json['last_name']
        if 'birth_date' in request.json:
            birth_date = validate_date(request.json['birth_date'])
            pupil_obj.birth_date = birth_date
        db.session.commit()
        return pupil_schema.dump(pupil_obj)

    def delete(self, pupil_id):
        pupil = Pupil.query.get_or_404(pupil_id)
        db.session.delete(pupil)
        db.session.commit()
        return '', 204


class PupilSingleAddToClassResource(Resource):

    def patch(self, pupil_id, class_id):
        pupil_obj = Pupil.query.get_or_404(pupil_id, description=f"Pupil with id {pupil_id} not found.")
        class_obj = SchoolClass.query.get_or_404(class_id, description=f"School Class with id {class_id} not found.")
        pupil_obj.school_class_id = class_obj.id
        db.session.commit()
        return {"message": f"Pupil has been assigned to {class_obj.name} class.",
                "pupil": pupil_schema.dump(pupil_obj)}, 200

    def put(self, pupil_id, class_id):
        pupil_obj = Pupil.query.get_or_404(pupil_id, description=f"Pupil with id {pupil_id} not found.")
        class_obj = SchoolClass.query.get_or_404(class_id, description=f"School Class with id {class_id} not found.")
        if class_obj.id == pupil_obj.school_class_id:
            abort(404, message="Pupil is in the same class already.")
        pupil_obj.school_class_id = class_obj.id
        db.session.commit()
        return {"message": f"Pupil's class has been changed to {class_obj.name} class.",
                "pupil": pupil_schema.dump(pupil_obj)}, 200


api.add_resource(PupilListResource, '/api/pupils/')
api.add_resource(SchoolClassListResource, '/api/classes/')
api.add_resource(PupilSingleResource, '/api/pupils/<int:pupil_id>/')
api.add_resource(PupilSingleAddToClassResource, '/api/pupils/<int:pupil_id>/<int:class_id>/')


@app.route('/', methods=['GET'])
def index_page():
    response = jsonify('Hello World!!!')
    response.status_code = 200

    return response


if __name__ == '__main__':
    app.run(debug=True)
