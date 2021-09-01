import uuid
import time
import re
import bcrypt
from db import get_db
from models.response import post_error
import jwt
import secrets
from utilities import MODULE_CONTEXT
from .app_enums import EnumVals
import config
import json
from datetime import datetime,timedelta
import requests
from flask_mail import Mail, Message
from app import mail
from flask import render_template
from collections import Counter
from config import USR_MONGO_COLLECTION,USR_TEMP_TOKEN_MONGO_COLLECTION,USR_KEY_MONGO_COLLECTION
import logging

log = logging.getLogger('file')

SECRET_KEY          =   secrets.token_bytes()

role_codes_filepath =   config.ROLE_CODES_URL
json_file_dir       =   config.ROLE_CODES_DIR_PATH
json_file_name      =   config.ROLE_CODES_FILE_NAME

mail_server         =   config.MAIL_SETTINGS["MAIL_USERNAME"]
mail_ui_link        =   config.BASE_URL
reset_pwd_link      =   config.RESET_PWD_ENDPOINT
token_life          =   config.AUTH_TOKEN_EXPIRY_HRS
verify_mail_expiry  =   config.USER_VERIFY_LINK_EXPIRY
apikey_expiry       =   config.USER_API_KEY_EXPIRY  
role_codes          =   []
role_details        =   []

class UserUtils:

    @staticmethod
    def generate_user_id():
        """UUID generation."""

        return(uuid.uuid4().hex)


    @staticmethod
    def validate_email_format(email):
        """Email validation

        Max length check
        Regex validation for emails.
        """
        if len(email) > config.EMAIL_MAX_LENGTH:
            return False
        regex = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
        if (re.search(regex, email)):
            return True
        else:
            return False


    @staticmethod
    def hash_password(password):
        """Password hashing using bcrypt."""

        # converting str to byte before hashing
        password_in_byte    = bytes(password, 'utf-8')  
        salt                = bcrypt.gensalt()
        return(bcrypt.hashpw(password_in_byte, salt))


    @staticmethod
    def validate_password(password):
        """Password rule check

        Minimum x chars long,as defined by 'MIN_LENGTH' on config,
        Must contain upper,lower,number and a special character.
        """

        if len(password) < config.PWD_MIN_LENGTH:
            return post_error("Invalid password", "password should be minimum {} characteristics long".format(config.PWD_MIN_LENGTH), None)
        if len(password) > config.PWD_MAX_LENGTH:
            return post_error("Invalid password", "password cannot exceed {} characteristics long".format(config.PWD_MAX_LENGTH), None)
        regex   = ("^(?=.*[a-z])(?=." + "*[A-Z])(?=.*\\d)" +
                 "(?=.*[-+_!@#$%^&*., ?]).+$")
        pattern = re.compile(regex)
        if re.search(pattern, password) is None:
            return post_error("Invalid password", "password must contain atleast one uppercase,one lowercase, one numeric and one special character", None)


    @staticmethod
    def validate_phone(phone):
        """Phone number validation
        
        10 digits, starts with 6,7,8 or 9.
        """
        pattern = re.compile("(0/91)?[6-9][0-9]{9}")
        if (pattern.match(phone)) and len(phone) == 10:
            return True
        else:
            return False

    @staticmethod
    def email_availability(email):
        """Email validation
        
        Verifying whether the email is already taken or not
        """
        try:
            #connecting to mongo instance/collection
            collections = get_db()[USR_MONGO_COLLECTION]  
            #searching username with verification status = True 
            user_record = collections.find({"email": email}) 
            if user_record.count() != 0:
                for usr in user_record:
                    if usr["isVerified"] == True:
                        log.info("Email is already taken")
                        return post_error("Data not valid", "This email address is already registered with ULCA. Please use another email address.", None)
                    register_time = usr["registeredTime"]
                    #checking whether verfication link had expired or not
                    if (datetime.utcnow() - register_time) < timedelta(hours=verify_mail_expiry):
                        log.exception("{} already did a signup, asking them to revisit their mail for verification".format(email))
                        return post_error("Data Not valid","This email address is already registered with ULCA. Please click on the verification link sent on your email address to complete the verification process.",None)
                    elif (datetime.utcnow() - register_time) > timedelta(hours=verify_mail_expiry):
                        #Removing old records if any
                        collections.delete_many({"email": email})
                    
            log.info("Email is not already taken, validated")
        except Exception as e:
            log.exception("Database connection exception |{}".format(str(e)))
            return post_error("Database exception", "An error occurred while working on the database:{}".format(str(e)), None)

    @staticmethod
    def validate_rolecodes(roles):
        """Role Validation

        roles should match roles defined on ULCA system,
        pre-defined roles are read from zuul (git) configs.
        """

        global role_codes
        global role_details
        if not role_codes:
            log.info("Reading roles from remote location")
            role_codes,role_details = UserUtils.read_role_codes()
        for role in roles:
            try:
                if role not in role_codes:
                    return False
            except Exception:
                return post_error("Roles missing","No roles are read from json,empty json or invalid path",None)


    @staticmethod
    def generate_api_keys(email):
        """Issuing new API key

        Generating public and private keys,
        storing them on redis,
        returning it back to users after successful storage.
        """
        
        try: 
            #creating payload for API Key storage
            key_payload = {"email": email, "publicKey":str(uuid.uuid4()), "privateKey": uuid.uuid4().hex, "createdOn": datetime.utcnow()}
            log.info("New API key issued for {}".format(email), MODULE_CONTEXT) 
            #connecting to mongo instance/collection
            collections = get_db()[USR_KEY_MONGO_COLLECTION]
            #inserting api-key records on db
            collections.insert(key_payload)
            del key_payload["_id"]
            del key_payload["createdOn"]
            return key_payload

        except Exception as e:
            log.exception("Database exception | {}".format(str(e)))
            return post_error("Database connection exception", "An error occurred while connecting to database :{}".format(str(e)), None)


    @staticmethod
    def token_validation(token):
        """Auth-token Validation for auth-token-search
        
        matching with existing active tokens on database,
        decoding the token,
        updating user token status on database in case of token expiry.
        """
        try:
            #connecting to mongo instance/collection
            collections = get_db()[USR_TOKEN_MONGO_COLLECTION]  
            #searching for token from database    
            result = collections.find({"token": token},{"_id": 0, "user": 1, "active": 1, "secret_key": 1})
            if result.count() == 0:
                log.info("No token found matching the auth-token-search request")
                return post_error("Invalid token", "Token received is not matching", None)
            for value in result:
                #checking for token status = False 
                if value["active"] == False:
                    log.info("Token on auth-token-search request has expired")
                    return post_error("Invalid token", "Token has expired", None)
                #checking for token status = True 
                if value["active"] == True:
                    secret_key = value["secret_key"]
                    #token decoding
                    try:
                        jwt.decode(token, secret_key, algorithm='HS256')
                    except jwt.exceptions.ExpiredSignatureError as e:
                        log.exception("Auth-token expired, time limit exceeded",  MODULE_CONTEXT, e)
                        #updating user token status on collection
                        collections.update({"token": token}, {"$set": {"active": False}})
                        return post_error("Invalid token", "Token has expired", None)
                    except Exception as e:
                        log.exception("Auth-token expired, jwt decoding failed",  MODULE_CONTEXT, e)
                        return post_error("Invalid token", "Not a valid token", None)
        except Exception as e:
            log.exception("Database connection exception ",  MODULE_CONTEXT, e)
            return post_error("Database connection exception", "An error occurred while connecting to the database", None)


    @staticmethod
    def get_user_from_token(token,temp):
        """Fetching user details from token"""

        try: 
            #for password resetting
            if temp:
                document = USR_TEMP_TOKEN_MONGO_COLLECTION 
                #connecting to mongo instance/collection
                collections = get_db()[document] 
                #searching for database record matching token, getting user_name
                result = collections.find({"token": token}, {"_id": 0, "user": 1})
                if result.count() == 0:
                    return post_error("Invalid token", "Token received is not matching", None)
                for record in result:
                    username = record["user"]  
            else:
                #connecting to redis instance
                redis_client = get_redis()
                key_data     = redis_client.get(token)
                usr_payload  = json.loads(key_data.decode("utf-8"))

        except Exception as e:
            log.exception("db connection exception ",  MODULE_CONTEXT, e)
            return post_error("Database connection exception", "An error occurred while connecting to the database", None)
        try:
            #connecting to mongo instance/collection
            collections_usr = get_db()[USR_MONGO_COLLECTION]
            #searching for database record matching username
            result_usr = collections_usr.find({"email": usr_payload["email"],"is_verified":True}, {"_id": 0, "password": 0})
            for record in result_usr:
                #checking active status of user
                if record["is_active"] == False:
                    log.info("{} is not an active user".format(username),MODULE_CONTEXT)
                    return post_error("Not active", "This operation is not allowed for an inactive user", None)
                return record
        except Exception as e:
            log.exception("db connection exception ",  MODULE_CONTEXT, e)
            return post_error("Database connection exception", "An error occurred while connecting to the database", None)


    @staticmethod
    def get_data_from_keybase(value,keys=None,email=None):
        try: 
            
            #connecting to mongo instance/collection
            collections = get_db()[USR_KEY_MONGO_COLLECTION] 
            if keys:
                result = collections.find({"email":value},{"email":1,"publicKey":1,"privateKey":1,"_id":0})
                if result.count() ==0:
                    return None
                for key in result:
                    return key  
            if email:
                result = collections.find({"publicKey":value},{"email":1,"privateKey":1,"createdOn":1,"_id":0})
                if result.count() ==0:
                    log.info("No data found matching the request")
                    return post_error("Invalid key", "key received is invalid", None)
                for key in result:
                    if ((datetime.utcnow() - key["createdOn"]) > timedelta(days=apikey_expiry)):
                        log.info("Keys expired for user : {}".format(key["email"]))
                        #removing keys since they had expired
                        collections.remove({"publicKey":value})
                        return post_error("Invalid key", "key has expired", None)
                    else:
                        return key

        except Exception as e:
            log.exception("db connection exception | {}".format(str(e)))
            return post_error("Database connection exception", "An error occurred while connecting to the database", None)
        

    @staticmethod
    def get_token(user_name):
        """Token Retrieval for login 
        
        fetching token for the desired user_name,
        validating the token(user_name matching, expiry check),
        updating the token status on db if the token had expired.
        """
        try:
            #connecting to mongo instance/collection
            collections = get_db()[USR_TOKEN_MONGO_COLLECTION] 
            #searching for token against the user_name
            record = collections.find({"user": user_name, "active": True}, {"_id": 0, "token": 1, "secret_key": 1})
            if record.count() == 0:
                log_info("No active token found for:{}".format(user_name), MODULE_CONTEXT)
                return {"status": False, "data": None}
            else:
                for value in record:
                    secret_key = value["secret_key"]
                    token = value["token"]
                    try:
                        #decoding the jwt token using secret-key
                        jwt.decode(token, secret_key, algorithm='HS256')
                        log_info("Token validated for:{}".format(user_name), MODULE_CONTEXT)
                        return({"status": True, "data": token})
                    #expired-signature error
                    except jwt.exceptions.ExpiredSignatureError as e:
                        log_exception("Token for {} had expired, exceeded the timeLimit".format(user_name),  MODULE_CONTEXT, e)
                        #updating token status on token-collection
                        collections.update({"token": token}, { "$set": {"active": False}})
                        return({"status": False, "data": None})
                    #falsy token error
                    except Exception as e:
                        log_exception("Token not valid for {}".format(user_name),  MODULE_CONTEXT, e)
                        return({"status": False, "data": None})
        except Exception as e:
            log.exception("Database connection exception ",  MODULE_CONTEXT, e)
            return({"status": "Database connection exception", "data": None})


    @staticmethod
    def validate_user_input_creation(user):
        """Validating user creation inputs.

        -Mandatory key checks
        -Email Validation
        -Password Validation 
        """
        obj_keys = {'firstName','email','password'}
        for key in obj_keys:
            if (user.get(key) == None) :
                    log.info("Mandatory key checks failed")
                    return post_error("Data Missing","firstName,email and password are mandatory for user creation",None)
        log.info("Mandatory key checks successful")

        if len(user["firstName"]) > config.NAME_MAX_LENGTH:
            return post_error("Invalid data", "firstName given is too long", None)
        email_availability_status = UserUtils.email_availability(user["email"])
        if email_availability_status is not None:
            log.info("Email validation failed, already taken")
            return email_availability_status
        if (UserUtils.validate_email_format(user["email"]) == False):
            log.info("Email validation failed")
            return post_error("Data not valid", "Email given is not valid", None)
        log.info("Email  validated")

        password_validity = UserUtils.validate_password(user["password"])
        if password_validity is not None:
            log.info("Password validation failed")
            return password_validity
        log.info("Password validated")

        if user.get("roles") != None:
            rolecodes = user["roles"]
            if UserUtils.validate_rolecodes(rolecodes) == False:
                log.info("Role validation failed")
                return post_error("Invalid data", "Rolecode given is not valid", None) 
            log.info("Role/s validated")

        if user.get("phoneNo") != None:
            phone_validity = UserUtils.validate_phone(user["phoneNo"])          
            if phone_validity is False:
                return post_error("Data not valid", "Phone number given is not valid", None)
        log.info("Phone number  validated")



    @staticmethod
    def validate_user_input_updation(user):
        """Validating user updation inputs.

        -Mandatory key checks
        -User Id Validation
        -Email Validation
        -Org Validation
        -Role Validation
        -Model Validation 
        """
        global role_details
        if user.get("userID") == None:
            return post_error("Data Missing", "userID not found", None)
        user_id = user["userID"]
        
        try:
            #connecting to mongo instance/collection
            collections = get_db()[USR_MONGO_COLLECTION]
            #searching User Id with verification status = True 
            record = collections.find({'userID': user_id,"is_verified":True})
            if record.count() == 0:
                log_info("User Id validation failed, no such user", MODULE_CONTEXT)
                return post_error("Data not valid", "No such verified user with the given Id", None)
            for value in record:
                if value["is_active"]== False:
                    log_info("User Id validation failed,inactive user", MODULE_CONTEXT)
                    return post_error("Not active", "This operation is not allowed for an inactive user", None)
            log_info("User Id validation successful", MODULE_CONTEXT)          
        except Exception as e:
            log_exception("Database connection exception ",  MODULE_CONTEXT, e)
            return post_error("Database connection exception", "An error occurred while connecting to the database:{}".format(str(e)), None)

        if user.get("email") != None:
            email_availability_status = UserUtils.email_availability(user["email"])
            if email_availability_status is not None:
                log_info("Email validation failed, already taken", MODULE_CONTEXT)
                return email_availability_status
            email_validity = UserUtils.validate_email_format(user["email"])
            if email_validity == False:
                log_info("Email validation failed, format error", MODULE_CONTEXT)
                return post_error("Data not valid", "Email Id given is not valid", None)  
            log_info("Email validated", MODULE_CONTEXT) 

        rolecodes=[]
        if user.get("roleCode") != None:
            rolecodes.append(str(user["roleCode"]))
            role_validity = UserUtils.validate_rolecodes(rolecodes) 
            if role_validity == False:
                log_info("Role validation failed", MODULE_CONTEXT)
                return post_error("Invalid data", "Rolecode given is not valid", None)
            log_info("Role validated", MODULE_CONTEXT)
            user["roles_new"]=[]
            roles_to_update={}
            roles_to_update["roleCode"]=str(user["roleCode"]).upper()
            role_desc=[x["description"] for x in role_details if x["code"]==user["roleCode"] ]
            roles_to_update["roleDesc"]=role_desc[0]
            user["roles_new"].append(roles_to_update)

       


    @staticmethod
    def validate_user_login_input(user_email, password):
        """User credentials validation
        
        checking whether the user is verified and active,
        password matching.
        """

        try:
            #connecting to mongo instance/collection
            collections = get_db()[USR_MONGO_COLLECTION]
            #fetching the user details from db
            result = collections.find({'email': user_email}, {
                'password': 1, '_id': 0,'isActive':1,'isVerified':1})
            if result.count() == 0:
                log.info("{} is not a verified user".format(user_email), MODULE_CONTEXT)
                return post_error("Not verified", "This email address is not registered with ULCA. Please sign up.", None)
            for value in result:
                if value["isVerified"]== False:
                    log.info("{} is not a verified user".format(user_email), MODULE_CONTEXT)
                    return post_error("Not active", "User account is not verified. Please click on the verification link sent on your email address to complete the verification process.", None)
                if value["isActive"]== False:
                    log.info("{} is not an active user".format(user_email), MODULE_CONTEXT)
                    return post_error("Not active", "This operation is not allowed for an inactive user", None)
                password_in_db = value["password"].encode("utf-8")
                try:
                    if bcrypt.checkpw(password.encode("utf-8"), password_in_db)== False:
                        log.info("Password validation failed for {}".format(user_email), MODULE_CONTEXT)
                        return post_error("Invalid Credentials", "Incorrect username or password", None)
                except Exception as e:
                    log.exception("exception while decoding password",  MODULE_CONTEXT, e)
                    return post_error("exception while decoding password", "exception:{}".format(str(e)), None)                   
        except Exception as e:
            log.exception(
                "Exception while validating email and password for login"+str(e),  MODULE_CONTEXT, e)
            return post_error("Database exception","Exception occurred:{}".format(str(e)),None)


    @staticmethod
    def read_role_codes():
        """Reading roles from git config."""
        
        try:
            file = requests.get(role_codes_filepath, allow_redirects=True)
            file_path = json_file_dir + json_file_name
            open(file_path, 'wb').write(file.content)
            log.info("Roles data read from git and pushed to local" )
            with open(file_path, 'r') as stream:
                parsed = json.load(stream)
                roles = parsed['roles']
                rolecodes = []
                role_details=[]
                for role in roles:
                    if role["active"]:
                        rolecodes.append(role["code"])
                        role_details.append(role)
            return rolecodes,role_details
        except Exception as exc:
            log.exception("Exception while reading roles: " +
                          str(exc), MODULE_CONTEXT, exc)
            return post_error("CONFIG_READ_ERROR",
                       "Exception while reading roles: " + str(exc), MODULE_CONTEXT)


    @staticmethod
    def generate_email_notification(user_records,task_id):

        for user_record in user_records:
            email       =   user_record["email"]
            timestamp   =   eval(str(time.time()).replace('.', '')[0:13])
            name        =   None
            user_id     =   None
            pubKey      =   None
            pvtKey      =   None
            link        =   None

            if task_id == EnumVals.VerificationTaskId.value:
                email_subject   =   EnumVals.VerificationSubject.value
                template        =   'usr_verification.html' 
                user_id         =   user_record["userID"]
                link            =   mail_ui_link+"activate/{}/{}/{}".format(email,user_id,timestamp)

            if task_id == EnumVals.ConfirmationTaskId.value:
                email_subject   =   EnumVals.ConfirmationSubject.value
                template        =   'usr_confirm_registration.html'
                name            =   user_record["name"]

            if task_id == EnumVals.ForgotPwdTaskId.value:
                email_subject   =   EnumVals.ForgotPwdSubject.value
                template        =   'reset_pwd_mail_template.html'
                pubKey          =   user_record["pubKey"]
                pvtKey          =   user_record["pvtKey"]
                link            =   mail_ui_link+reset_pwd_link+"{}/{}/{}/{}".format(email,pubKey,pvtKey,timestamp)
                name            =   user_record["name"]
            try:
                msg = Message(subject=email_subject,sender=mail_server,recipients=[email])
                msg.html = render_template(template,ui_link=mail_ui_link,activity_link=link,user_name=name)
                mail.send(msg)
                log.info("Generated email notification for {} ".format(email), MODULE_CONTEXT)
            except Exception as e:
                log.exception("Exception while generating email notification | {}".format(str(e)))
                return post_error("Exception while generating email notification","Exception occurred:{}".format(str(e)),None)
            
    @staticmethod
    def validate_username(user_email):
        """Validating userName/Email"""

        try:
            #connecting to mongo instance/collection
            collections = get_db()[USR_MONGO_COLLECTION]
            #searching for record matching user_name
            valid = collections.find({"email":user_email,"isVerified":True})
            if valid.count() == 0:
                log.info("Not a valid email/username")
                return post_error("Not Valid","This email address is not registered with ULCA",None)#Given email is not associated with any of the active ULCA accounts
            for value in valid:
                if value["isActive"]== False:
                    log.info("Given email/username is inactive")
                    return post_error("Not active", "This operation is not allowed for an inactive user", None)
        except Exception as e:
            log.exception("exception while validating username/email"+str(e),  MODULE_CONTEXT, e)
            return post_error("Database exception","Exception occurred:{}".format(str(e)),None)




                

        
