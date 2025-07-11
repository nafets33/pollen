import jwt
import bcrypt
import streamlit as st
import time
from datetime import datetime, timedelta
from pytz import timezone
import extra_streamlit_components as stx
import ipdb

from .hasher import Hasher
from .utils import generate_random_pw

from .exceptions import (
    CredentialsError,
    ResetError,
    RegisterError,
    ForgotError,
    UpdateError,
)


class Authenticate:
    """
    This class will create login, logout, register user, reset password, forgot password,
    forgot username, and modify user details widgets.
    """

    def __init__(
        self,
        credentials: dict,
        cookie_name: str,
        key: str,
        cookie_expiry_days: int = 30,
        preauthorized: list = None,
    ):
        """
        Create a new instance of "Authenticate".

        Parameters
        ----------
        credentials: dict
            The dictionary of usernames, names, passwords, and emails.
        cookie_name: str
            The name of the JWT cookie stored on the client's browser for passwordless reauthentication.
        key: str
            The key to be used for hashing the signature of the JWT cookie.
        cookie_expiry_days: int
            The number of days before the cookie expires on the client's browser.
        preauthorized: list
            The list of emails of unregistered users authorized to register.
        """
        self.credentials = credentials
        self.credentials["usernames"] = {
            key.lower(): value for key, value in credentials["usernames"].items()
        }
        self.cookie_name = cookie_name
        self.key = key
        self.cookie_expiry_days = cookie_expiry_days
        self.preauthorized = preauthorized
        self.cookie_manager = stx.CookieManager()

        if "name" not in st.session_state:
            st.session_state["name"] = None
        if "authentication_status" not in st.session_state:
            st.session_state["authentication_status"] = None
        if "username" not in st.session_state:
            st.session_state["username"] = None
        if "logout" not in st.session_state:
            st.session_state["logout"] = None

    def _token_encode(self) -> str:
        """
        Encodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The JWT cookie for passwordless reauthentication.
        """
        return jwt.encode(
            {
                "name": st.session_state["name"],
                "username": st.session_state["username"],
                "exp_date": self.exp_date,
            },
            self.key,
            algorithm="HS256",
        )

    def _token_decode(self) -> str:
        """
        Decodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The decoded JWT cookie for passwordless reauthentication.
        """
        try:
            return jwt.decode(self.token, self.key, algorithms=["HS256"])
        except:
            return False

    def _set_exp_date(self) -> str:
        """
        Creates the reauthentication cookie's expiry date.

        Returns
        -------
        str
            The JWT cookie's expiry timestamp in Unix epoch.
        """
        return (datetime.utcnow() + timedelta(days=self.cookie_expiry_days)).timestamp()

    def _check_pw(self) -> bool:
        """
        Checks the validity of the entered password.

        Returns
        -------
        bool
            The validity of the entered password by comparing it to the hashed password on disk.
        """
        return bcrypt.checkpw(
            self.password.encode(),
            self.credentials["usernames"][self.username]["password"].encode(),
        )

    def _check_cookie(self):
        """
        Checks the validity of the reauthentication cookie.
        """
        self.token = self.cookie_manager.get(self.cookie_name)
        if self.token is not None:
            self.token = self._token_decode()
            if self.token is not False:
                if not st.session_state["logout"]:
                    if self.token["exp_date"] > datetime.utcnow().timestamp():
                        if "name" and "username" in self.token:
                            username = self.token["username"]
                            if username in self.credentials["usernames"]:
                                # username is valid, continue
                                st.session_state["name"] = self.token["name"]
                                st.session_state["username"] = self.token["username"]
                                st.session_state["authentication_status"] = True
                                self.credentials["usernames"][st.session_state["username"]]["login_count"] = (
                                    int(self.credentials["usernames"][st.session_state["username"]]["login_count"]) + 1
                                )
                                self.credentials["usernames"][st.session_state["username"]]["last_login_date"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                                st.sidebar.write(f"Welcome *{st.session_state['name']}*")
                                st.session_state["logout"] = False

                            else:
                                # username not found -> clear cookie and reset session
                                self.cookie_manager.delete(self.cookie_name)
                                st.session_state["authentication_status"] = None
                                if "name" in st.session_state:
                                    del st.session_state["name"]
                                if "username" in st.session_state:
                                    del st.session_state["username"]
                                st.session_state["logout"] = True

    def _check_credentials(self, inplace: bool = True) -> bool:
        """
        Checks the validity of the entered credentials.

        Parameters
        ----------
        inplace: bool
            Inplace setting, True: authentication status will be stored in session state,
            False: authentication status will be returned as bool.
        Returns
        -------
        bool
            Validity of entered credentials.
        """
        if self.username in self.credentials["usernames"]:
            try:
                if self._check_pw():
                    if inplace:
                        st.session_state["name"] = self.credentials["usernames"][
                            self.username
                        ]["name"]
                        self.exp_date = self._set_exp_date()
                        self.token = self._token_encode()
                        self.cookie_manager.set(
                            self.cookie_name,
                            self.token,
                            expires_at=datetime.now()
                            + timedelta(days=self.cookie_expiry_days),
                        )
                        st.session_state["authentication_status"] = True
                    else:
                        return True
                else:
                    if inplace:
                        st.session_state["authentication_status"] = False
                    else:
                        return False
            except Exception as e:
                print(e)
        else:
            if inplace:
                st.session_state["authentication_status"] = False
            else:
                return False

    def direct_login(self, email, password):
        self.username = email
        self.password = password
        st.session_state["username"] = self.username
        print(" DIRECT auth!!", email)
        # if st.session_state["username"] in st.session_state['auth_email']:
        #     return (
        #         st.session_state["name"],
        #         True,
        #         st.session_state["username"],
        #     )

        self._check_credentials()

        return (
            st.session_state["name"],
            st.session_state["authentication_status"],
            st.session_state["username"],
        )

    def login(self, form_name: str, location: str = "main") -> tuple:
        """
        Creates a login widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the login form.
        location: str
            The location of the login form i.e. main or sidebar.
        Returns
        -------
        str
            Name of the authenticated user.
        bool
            The status of authentication, None: no credentials entered,
            False: incorrect credentials, True: correct credentials.
        str
            Username of the authenticated user.
        """
        try:
            if location not in ["main", "sidebar"]:
                raise ValueError("Location must be one of 'main' or 'sidebar'")
            if not st.session_state["authentication_status"]:

                self._check_cookie()
                time.sleep(1)
                print(st.session_state["authentication_status"])
                if st.session_state["authentication_status"] != True:

                    if location == "main":
                        login_form = st.form("Login")
                    elif location == "sidebar":
                        login_form = st.sidebar.form("Login")

                    login_form.subheader(form_name)
                    self.username = login_form.text_input("Email").lower()
                    st.session_state["username"] = self.username
                    self.password = login_form.text_input("Password", type="password")

                    if login_form.form_submit_button("Login"):
                        self._check_credentials()

                        if st.session_state["authentication_status"]:
                            self.credentials["usernames"][st.session_state["username"]][
                                "login_count"
                            ] = (
                                int(
                                    self.credentials["usernames"][
                                        st.session_state["username"]
                                    ]["login_count"]
                                )
                                + 1
                            )
                            self.credentials["usernames"][st.session_state["username"]][
                                "last_login_date"
                            ] = datetime.now(timezone("EST")).strftime("%d/%m/%Y %H:%M")
                            st.sidebar.write(f"Welcome *{st.session_state['name']}*")
                            st.session_state["logout"] = False

            return (
                st.session_state["name"],
                st.session_state["authentication_status"],
                st.session_state["username"],
            )
        except Exception as e:
            import sys
            def print_line_of_error(e='print_error_message'):
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(e, exc_type, exc_tb.tb_lineno)
                return exc_type, exc_tb.tb_lineno
            print_line_of_error(e)
            st.session_state["name"] = 'ERROR'
            st.session_state["authentication_status"] = False
            st.session_state["username"] = 'ERROR'
            return (
                st.session_state["name"],
                st.session_state["authentication_status"],
                st.session_state["username"],
            )

    def logout(self, button_name: str, location: str = "main", use_container_width: bool=True):
        """
        Creates a logout button.

        Parameters
        ----------
        button_name: str
            The rendered name of the logout button.
        location: str
            The location of the logout button i.e. main or sidebar.
        """
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            # with st.expander('Logout'):
            if st.button(button_name,  use_container_width=use_container_width):
                self.cookie_manager.delete(self.cookie_name)
                st.session_state["logout"] = True
                st.session_state["name"] = None
                st.session_state["username"] = None
                st.session_state["authentication_status"] = None
        elif location == "sidebar":
            if st.sidebar.button(button_name,  use_container_width=use_container_width):
                self.cookie_manager.delete(self.cookie_name)
                st.session_state["logout"] = True
                st.session_state["name"] = None
                st.session_state["username"] = None
                st.session_state["authentication_status"] = None

    def _update_password(self, username: str, password: str):
        """
        Updates credentials dictionary with user's reset hashed password.

        Parameters
        ----------
        username: str
            The username of the user to update the password for.
        password: str
            The updated plain text password.
        """
        self.credentials["usernames"][username]["password"] = Hasher([password]).generate()[0]

    def reset_password(
        self, username: str, form_name: str, location: str = "main"
    ) -> bool:
        """
        Creates a password reset widget.

        Parameters
        ----------
        username: str
            The username of the user to reset the password for.
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        Returns
        -------
        str
            The status of resetting the password.
        """
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            with st.expander("reset password", False):
                reset_password_form = st.form("Reset password")
                reset_password_form.subheader(form_name)
                self.username = username.lower()
                self.password = reset_password_form.text_input(
                    "Current password", type="password"
                )
                new_password = reset_password_form.text_input(
                    "New password", type="password"
                )
                new_password_repeat = reset_password_form.text_input(
                    "Repeat password", type="password"
                )
        elif location == "sidebar":
            with st.sidebar.expander("reset password", False):
                reset_password_form = st.form("Reset password")
                reset_password_form.subheader(form_name)
                self.username = username.lower()
                self.password = reset_password_form.text_input(
                    "Current password", type="password"
                )
                new_password = reset_password_form.text_input(
                    "New password", type="password"
                )
                new_password_repeat = reset_password_form.text_input(
                    "Repeat password", type="password"
                )

        if reset_password_form.form_submit_button("Reset"):
            if self._check_credentials(inplace=False):
                if len(new_password) > 0:
                    if new_password == new_password_repeat:
                        if self.password != new_password:
                            self._update_password(self.username, new_password)
                            return True
                        else:
                            raise ResetError("New and current passwords are the same")
                    else:
                        raise ResetError("Passwords do not match")
                else:
                    raise ResetError("No new password provided")
            else:
                raise CredentialsError

    def _register_credentials(
        self,
        username: str,
        name: str,
        phone_no: str,
        password: str,
        signup_date: str,
        last_login_date: str,
        login_count: int,
        preauthorization: bool,
    ):
        """
        Adds to credentials dictionary the new user's information.

        Parameters
        ----------
        username: str
            The username of the new user.
        name: str
            The name of the new user.
        password: str
            The password of the new user.
        email: str
            The email of the new user.
        preauthorization: bool
            The pre-authorization requirement, True: user must be pre-authorized to register,
            False: any user can register.
        """

        user_detials = {
            "name": name,
            "phone_no": phone_no,
            "password": Hasher([password]).generate()[0],
            "signup_date": signup_date,
            "last_login_date": last_login_date,
            "login_count": login_count,
        }

        self.credentials["usernames"][username] = user_detials
        st.session_state["new_user_creds"] = user_detials

        if preauthorization:
            self.preauthorized["emails"].remove(username)

    def register_user(
        self, form_name: str, location: str = "main", preauthorization=True
    ) -> bool:
        """
        Creates a password reset widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        preauthorization: bool
            The pre-authorization requirement, True: user must be pre-authorized to register,
            False: any user can register.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """
        if not self.preauthorized:
            raise ValueError("Pre-authorization argument must not be None")
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            register_user_form = st.form("Register user")
        elif location == "sidebar":
            register_user_form = st.sidebar.form("Register user")

        register_user_form.subheader(form_name)
        new_username = register_user_form.text_input("Email").lower()
        new_name = register_user_form.text_input("Name")
        phone_no_cols = register_user_form.columns([1, 4])
        # new_country_code = phone_no_cols[0].selectbox(
        #     "Phone Number", ["US (+1)", "UK (+44)"]
        # )
        new_phone_no = phone_no_cols[1].text_input(" ", max_chars=10)
        new_phone_no = new_phone_no # new_country_code + new_phone_no
        new_password = register_user_form.text_input("Password", type="password")
        new_password_repeat = register_user_form.text_input(
            "Repeat password", type="password"
        )
        signup_date = datetime.now(timezone("EST")).strftime("%d/%m/%Y %H:%M")
        last_login_date = datetime.now(timezone("EST")).strftime("%d/%m/%Y %H:%M")
        login_count = 0

        if register_user_form.form_submit_button("Get Code"):
            if len(new_username) and len(new_name) and len(new_password) > 0:
                if new_username not in self.credentials["usernames"]:
                    if new_password == new_password_repeat:
                        if preauthorization:
                            if new_username in self.preauthorized["emails"]:
                                self._register_credentials(
                                    new_username,
                                    new_name,
                                    new_phone_no,
                                    new_password,
                                    signup_date,
                                    last_login_date,
                                    login_count,
                                    preauthorization,
                                )
                                return new_username, new_password
                            else:
                                raise RegisterError(
                                    "User not pre-authorized to register"
                                )
                        else:
                            self._register_credentials(
                                new_username,
                                new_name,
                                new_phone_no,
                                new_password,
                                signup_date,
                                last_login_date,
                                login_count,
                                preauthorization,
                            )
                            return new_username, new_password
                    else:
                        raise RegisterError("Passwords do not match")
                else:
                    raise RegisterError("Email already exists")
            else:
                raise RegisterError("Please enter an email, name, and password")

    def _set_random_password(self, username: str) -> str:
        """
        Updates credentials dictionary with user's hashed random password.

        Parameters
        ----------
        username: str
            Username of user to set random password for.
        Returns
        -------
        str
            New plain text password that should be transferred to user securely.
        """
        self.random_password = generate_random_pw()
        self.credentials["usernames"][username]["password"] = Hasher(
            [self.random_password]
        ).generate()[0]
        return self.random_password

    def forgot_password(self, form_name: str, location: str = "main") -> tuple:
        """
        Creates a forgot password widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the forgot password form.
        location: str
            The location of the forgot password form i.e. main or sidebar.
        Returns
        -------
        str
            Username associated with forgotten password.
        str
            Email associated with forgotten password.
        str
            New plain text password that should be transferred to user securely.
        """
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            forgot_password_form = st.form("Forgot password")
        elif location == "sidebar":
            forgot_password_form = st.sidebar.form("Forgot password")

        forgot_password_form.subheader(form_name)
        username = forgot_password_form.text_input("Email").lower()

        if forgot_password_form.form_submit_button("Submit"):
            if len(username) > 0:
                if username in self.credentials["usernames"]:
                    return username, self._set_random_password(username)
                else:
                    return False, None
            else:
                raise ForgotError("Username not provided")
        return None, None

    def _get_username(self, key: str, value: str) -> str:
        """
        Retrieves username based on a provided entry.

        Parameters
        ----------
        key: str
            Name of the credential to query i.e. "email".
        value: str
            Value of the queried credential i.e. "jsmith@gmail.com".
        Returns
        -------
        str
            Username associated with given key, value pair i.e. "jsmith".
        """
        for username, entries in self.credentials["usernames"].items():
            if entries[key] == value:
                return username
        return False

    def _forgot_username(self, form_name: str, location: str = "main") -> tuple:
        """
        Creates a forgot username widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the forgot username form.
        location: str
            The location of the forgot username form i.e. main or sidebar.
        Returns
        -------
        str
            Forgotten username that should be transferred to user securely.
        str
            Email associated with forgotten username.
        """
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            forgot_username_form = st.form("Forgot username")
        elif location == "sidebar":
            forgot_username_form = st.sidebar.form("Forgot username")

        forgot_username_form.subheader(form_name)
        email = forgot_username_form.text_input("Email")

        if forgot_username_form.form_submit_button("Submit"):
            if len(email) > 0:
                return self._get_username("email", email), email
            else:
                raise ForgotError("Email not provided")
        return None, email

    def _update_entry(self, username: str, key: str, value: str):
        """
        Updates credentials dictionary with user's updated entry.

        Parameters
        ----------
        username: str
            The username of the user to update the entry for.
        key: str
            The updated entry key i.e. "email".
        value: str
            The updated entry value i.e. "jsmith@gmail.com".
        """
        self.credentials["usernames"][username][key] = value

    def update_user_details(
        self, username: str, form_name: str, location: str = "main"
    ) -> bool:
        """
        Creates a update user details widget.

        Parameters
        ----------
        username: str
            The username of the user to update user details for.
        form_name: str
            The rendered name of the update user details form.
        location: str
            The location of the update user details form i.e. main or sidebar.
        Returns
        -------
        str
            The status of updating user details.
        """
        if location not in ["main", "sidebar"]:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == "main":
            update_user_details_form = st.form("Update user details")
        elif location == "sidebar":
            update_user_details_form = st.sidebar.form("Update user details")

        update_user_details_form.subheader(form_name)
        self.username = username.lower()
        field = update_user_details_form.selectbox("Field", ["Name"]).lower()
        new_value = update_user_details_form.text_input("New value")

        if update_user_details_form.form_submit_button("Update"):
            if len(new_value) > 0:
                if new_value != self.credentials["usernames"][self.username][field]:
                    self._update_entry(self.username, field, new_value)
                    if field == "name":
                        st.session_state["name"] = new_value
                        self.exp_date = self._set_exp_date()
                        self.token = self._token_encode()
                        self.cookie_manager.set(
                            self.cookie_name,
                            self.token,
                            expires_at=datetime.now()
                            + timedelta(days=self.cookie_expiry_days),
                        )
                    return True
                else:
                    raise UpdateError("New and current values are the same")
            if len(new_value) == 0:
                raise UpdateError("New value not provided")
