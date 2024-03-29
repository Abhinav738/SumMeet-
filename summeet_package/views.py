import os
from flask import Blueprint, Response, Flask, session
from flask import request, render_template, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, request
from summeet_package.models import users
from werkzeug.security import generate_password_hash, check_password_hash
from summeet_package import db, create_app, app
from werkzeug.utils import secure_filename
from summeet_package.models import uploaded_files
# from summeet_package.models import advt_approval
# import rec_sys as model

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['mp3', 'wav', 'mp4'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('index.html')


@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        user_email = request.form.get("user_email")
        age = request.form.get("age")
        pswd1 = request.form.get("pswd1")
        gender = request.form["gender"]
        # max_id = db.session.query(users).order_by(users.id.desc()).first()

        user = users.query.filter_by(user_email=user_email).first()
        if user:
            flash('Email already exists.', category='error')
            return render_template('user-registration.html')
        else:
            hashed_password = generate_password_hash(
                pswd1, method='sha256')
            user_regis = users(fname=fname, lname=lname, 
            user_email=user_email, password=hashed_password, 
            age=age, gender=gender)
            db.session.add(user_regis)
            db.session.commit()
            flash('Account created! Please login', category='success')
            return redirect(url_for('views.login'))
    return render_template('user-registration.html')

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pswd')
        user = users.query.filter_by(user_email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect('/user/dashboard')
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist', category='error')
    return render_template('login.html')


@views.route('/logout')
@login_required
def logout():
    logout_user()
    flash("logged out successfully!", category='success')
    return redirect(url_for('views.home'))


@views.route('/user/dashboard', methods = ['GET', 'POST'])
@login_required
def user_dashboard():
    if current_user.fname == None:
        flash('Please login')
        return redirect(url_for('views.login'))
    else:
        name = current_user.fname
        # recmd_infl = model.recm_sys(name)
        # owner_id = current_user.id
        # advts_owner= uploaded_files.query.all()
        # advts = uploaded_files.query.filter_by(owner_id=owner_id)
        # advts_oid = uploaded_files.query.filter_by(owner_id=owner_id).first()
        # recmd_infl.remove(owner_id)
        # main=[]
        # for inf_id in recmd_infl:
        #     inf = users.query.filter_by(id=inf_id)
        #     for infl in inf:
        #         f = infl.fname
        #         l = infl.lname
        #         c = infl.categories
        #         s = infl.smh
        #         n = infl.infl_pic
        #         abc=[]
        #         abc.append(f)
        #         abc.append(l)
        #         abc.append(c)
        #         abc.append(s)
        #         abc.append(n)
        #         main.append(abc)
        # print(main)
        # try:
        #     # adv_oid = advts_oid.owner_id
        #     if adv_oid:
        #         return render_template('user_dashboard.html', name=name, advts_owner=advts_owner, adv_oid=adv_oid, owner_id=owner_id,main = main)
        #     else:
        #         return render_template('user_dashboard.html',advts=advts, name=name, advts_owner=advts_owner, owner_id=owner_id, main = main)
        # except:
        return render_template('user_dashboard.html', name=name)


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/user/upload', methods = ['GET', 'POST'])
@login_required
def user_upload():
    if current_user.fname == None:
        flash('Please login')
        return redirect(url_for('views.login'))
    else:
        if request.method == 'POST':
            files = request.files.getlist('mtng_file')
            for file in files:
                if file and allowed_file(file.filename):
                    user_fname = current_user.fname
                    email = current_user.user_email
                    mailing_list = request.form.get('mailing_list')
                    meeting_agenda = request.form.get('meeting_agenda')
                    mtng_file = request.files['mtng_file']
                    owner_id = current_user.id
                    
                    filename = secure_filename(mtng_file.filename)
                    mimetype = mtng_file.mimetype
                    
                    file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                    advt = uploaded_files(owner_id=owner_id, user_fname=user_fname, mailing_list=mailing_list, meeting_agenda=meeting_agenda,
                    name = filename, mimetype=mimetype)
                    db.session.add(advt)
                    db.session.commit()
                    flash('File uploaded!', category='success')
                    return redirect(url_for('views.user_dashboard'))
                else:
                    flash('Please upload a valid file (mp3/mp4/wav).')
                    user_email=current_user.user_email
                    user_name = current_user.fname
                    return render_template('user_upload.html',user_email=user_email, user_name=user_fname)
        
        user_email=current_user.user_email
        user_name = current_user.fname
        return render_template('user_upload.html', user_email=user_email, user_name=user_name)

@views.route('/advt/update_advertise/<int:id>', methods = ['GET', 'POST'])
@login_required
def advt_update(id):
    name_to_update = uploaded_files.query.filter(uploaded_files.id==id).first()
    advt = uploaded_files.query.filter_by(id=id).first()
    advt_name_update = uploaded_files.query.filter_by(id=id).first()
    files = request.files.getlist('prdt_imgs')
    for file in files:
        if file and allowed_file(file.filename):
            name_to_update.desc = request.form.get('desc')
            name_to_update.brand = request.form.get('brand')
            name_to_update.deadline = request.form.get('deadline')
            name_to_update.prdt_sp = request.form.get('prdt_sp')
            name_to_update.age_grp = request.form.get('age_grp')
            name_to_update.prdt_imgs = request.files['prdt_imgs']
            filename = secure_filename(name_to_update.prdt_imgs.filename)  
            name_to_update.name = filename
            advt_name_update.advt_name = filename
            try:
                file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                db.session.commit()                    
                flash('Database updated successfully!')
                return redirect(url_for('views.advt_dashboard'))
            except:
                file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                db.session.commit()                    
                flash('Database updated successfully!')
                return redirect(url_for('views.advt_dashboard'))

    advt_id = id
    user_email = current_user.comp_email
    advts = uploaded_files.query.filter_by(id=advt_id).first()
    return render_template('advt_update_uploaded_files.html',advt=advt, advts=advts, user_email=user_email, id=advt_id )

# @views.route('/advt/delete_advertise/<int:id>')
# @login_required
# def advt_delete(id):
#     advt_to_delete = uploaded_files.query.get_or_404(id)
#     advta_to_delete = advt_approval.query.filter_by(advt_id=id).first()
#     try:
#         if advt_to_delete:
#             db.session.delete(advt_to_delete)
#             db.session.commit()
#         elif advta_to_delete:
#             db.session.delete(advta_to_delete)
#             db.session.commit()
#         flash('Advertisement deleted successfully!')
#         return redirect(url_for('views.advt_dashboard'))
#     except:
#         flash('some error occured')
#         return redirect(url_for('views.advt_dashboard'))


# @views.route('/advt/applications/<int:id>', methods = ['GET', 'POST'])
# @login_required
# def advt_apply(id):
#     advt_id = id    
#     apl = advt_approval.query.filter_by(advt_id=advt_id, approved=0).all()        
#     advts = uploaded_files.query.filter_by(id=advt_id).first()
#     return render_template('advt_applications.html', advt=advts,apl=apl)


# @views.route('/advt/approved_applications/<int:id>', methods = ['GET', 'POST'])
# @login_required
# def advt_app_applicants(id):
#     advt_id = id    
#     apl = advt_approval.query.filter_by(advt_id=advt_id, approved=1).all()        
#     advts = uploaded_files.query.filter_by(id=advt_id).first()
#     return render_template('advt_approved_applicants.html', advt=advts,apl=apl)


# @views.route('/advt/applications/approve/<int:id>', methods = ['GET', 'POST'])
# @login_required
# def advt_approve(id):
#     advt_apr = advt_approval.query.filter_by(id=id).first()
#     advt_apr.approved=1
#     advt_apr.filter='approved'
#     advta_id = advt_apr.advt_id
#     db.session.commit()
#     flash('Influencer application approved! Hope you have a great collaboartion!')
#     return redirect(url_for('views.advt_apply', id=advta_id))


# @views.route('/advt/applications/reject/<int:id>')
# @login_required
# def advt_reject(id):
#     advtr=advt_approval.query.filter_by(id=id)
#     advtr_id=advtr[0].advt_id
#     apply_to_delete = advt_approval.query.get_or_404(id)
#     try:
#         db.session.delete(apply_to_delete)
#         db.session.commit()
#         flash('Application rejected, hope you find a better candidate!')
#         return redirect(url_for('views.advt_apply', id=advtr_id))

#     except:
#         flash('some error occured ')
#         return redirect(url_for('views.advt_dashboard'))

# @views.route('/advt/advt_details/<int:advt_id>', methods = ['POST', 'GET'])
# @login_required
# def advt_details(advt_id):
#     advt = uploaded_files.query.filter_by(id=advt_id).first()
#     return render_template('advt_details.html', advt=advt)

@views.route('/adv_regis', methods=['GET', 'POST'])
def adv_regis():
    if request.method == 'POST':
        user_name = request.form.get("user_name")
        acc_handler_name = request.form.get("acc_handler_name")
        acc_handler_desig = request.form.get("acc_handler_desig")
        comp_website = request.form.get("comp_website")
        ph_no = request.form.get("ph_no")
        comp_email = request.form.get("comp_email")
        ah_email = request.form.get("ah_email")
        categories = request.form.get("advt_categories")
        pswd1 = request.form.get("pswd1")
        acc_handler_gender = request.form["gender"]
        acc_type = 'advt'
        # max_id = db.session.query(users).order_by(users.id.desc()).first()
        # id = db.session.query(users)
        # print(max_id.id)
        user = users.query.filter_by(comp_email=comp_email).first()
        if user:
            flash('Email already exists.', category='error')
            return render_template('advertiser-registration.html')
        else:
            hashed_password = generate_password_hash(
                pswd1, method='sha256')
            # if 
            # adv_regis_user = users(id=max_id.id+1, user_name=user_name, acc_handler_name=acc_handler_name,
            adv_regis_user = users(user_name=user_name, acc_handler_name=acc_handler_name,
            acc_handler_desig=acc_handler_desig, comp_website=comp_website, ph_no=ph_no, comp_email=comp_email,
            ah_email=ah_email, categories=categories,password=hashed_password, acc_handler_gender=acc_handler_gender, acc_type=acc_type)
            db.session.add(adv_regis_user)
            db.session.commit()
            flash('Account created! Please login', category='success')
            return redirect(url_for('views.login'))
    return render_template('advertiser-registration.html')


@views.route('/inf_regis', methods=['GET', 'POST'])
def inf_regis():
    if request.method == 'POST':
        file = request.files['infl_pic']
        if file and allowed_file(file.filename):
            fname = request.form.get("fname")
            lname = request.form.get("lname")
            smh = request.form.get("smh")
            ph_no = request.form.get("ph_no")
            inf_email = request.form.get("inf_email")
            categories = request.form.get("inf_categories")
            age = request.form.get("age")
            pswd1 = request.form.get("pswd1")
            infl_pic = request.files["infl_pic"]
            gender = request.form["gender"]
            acc_type = 'infl'
            max_id = db.session.query(users).order_by(users.id.desc()).first()
            filename = secure_filename(file.filename)
            print(filename)
            mimetype = infl_pic.mimetype

            file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))

            user = users.query.filter_by(inf_email=inf_email).first()
            if user:
                flash('Email already exists.', category='error')
                return render_template('influencer-registration.html')
            else:
                hashed_password = generate_password_hash(
                    pswd1, method='sha256')
                inf_regis_user = users(id=max_id.id+1, fname=fname, lname=lname, smh=smh,ph_no=ph_no, 
                inf_email=inf_email, categories=categories,password=hashed_password, 
                age=age, gender=gender, acc_type=acc_type, infl_pic = filename, mimetype=mimetype)
                db.session.add(inf_regis_user)
                db.session.commit()
                flash('Account created! Please login', category='success')
                return redirect(url_for('views.login'))
    return render_template('influencer-registration.html')
