#!/bin/bash

#set -xv
export PATH="$PATH:/usr/local/bin:/usr/local/sbin:/Applications/Xcode.app/Contents/Developer/usr/bin"

PROJECT_NAME='printer_portal'

GIT_REPO="https://github.com/eahrold/printer_portal-server.git"
GIT_BRANCH="master"

OSX_WEBAPP_PLIST="edu.loyno.smc.printer_portal.webapp.plist"
APACHE_SUBPATH="printers"

## you only need to set one of the following two requirements...
DJANGO_REQUIREMENTS_FILE="setup/requirements.txt"
#DJANGO_REQUIREMENTS=(Django django-bootstrap-toolkit, south, markdown2)

#### specify any insatlled apps whose db is managed by south
SOUTH_MANAGED_DJANGO_APPS=(printers sparkle)

OSX_CONF_FILE_DIR="OSX"

#### Below are configurations that probably don't need to change,
#### but can get over ridden for particular reasons
APP_DEFAULT_NAME=${PROJECT_NAME}
PROJECT_SETTINGS_DIR=${APP_DEFAULT_NAME}

APACHE_CONFIG_FILE="httpd_${APP_DEFAULT_NAME}.conf"
WSGI_FILE="${APP_DEFAULT_NAME}.wsgi"

USER_NAME="${APP_DEFAULT_NAME}"
GROUP_NAME="${APP_DEFAULT_NAME}"

VIRENV_NAME="${APP_DEFAULT_NAME}_env"

WEB_DATA_LOCATION=$(serveradmin settings web:dataLocation | awk '{print $3}'|sed s/\"//g)
OSX_SERVER_WSGI_DIR="${WEB_DATA_LOCATION}/WebApps/"
OSX_SERVER_SITES_DEFAULT="${WEB_DATA_LOCATION}/Sites/"
OSX_SERVER_APACHE_DIR="/Library/Server/Web/Config/apache2/"


function custom_precondition_check () {
    echo "running custom checks..."
# put any custom requirment checks here 
}

function custom_configuration () {
    echo "running custom configuration..."
    # put any custom configurations here 
}

function custom_apache_configuration () {    
    # put any app specific configurations here
    local media_root_alias="Alias /files_${PROJECT_NAME}/ ${MEDIA_ROOT}"

    if [ ${USER_NAME} == "www" ]; then
        echo "${media_root_alias}" >> "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        echo "" >> "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        echo "<Location /files_${PROJECT_NAME}/private/>" >> "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        echo "    Order Allow,Deny" >> "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        echo "    Deny from  all" >> "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        echo "</Location>" >> "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
    else        
        ised "Alias /files_${PROJECT_NAME}/" "${media_root_alias}" "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
    fi
}

function custom_clean_up () {
    local private_file_dir="${PROJECT_PATH}/${PROJECT_SETTINGS_DIR}/private/"
    if [ ! -d ${private_file_dir} ]; then
        mkdir -m 700 "${PROJECT_PATH}/${PROJECT_SETTINGS_DIR}/private/"
    fi
}

function prompt_for_settings () {
clear
cecho red    "##################################################################"
cecho red    "##########         django webapp installer            ############"
cecho red    "##################################################################"

cecho question "First we need to determine what user should own the webapp process" 

while true; do
cecho purple "[1] www user" "(if you plan to run on both http(80) and https(443))"
cecho purple "[2] create a user ${USER_NAME} and group ${GROUP_NAME}"
    read -e -p "Please Select: " -n 1 -r
    if [[ $REPLY -eq 2 ]];then
        make_user_and_group
        if [ $? == 0 ]; then
            break
        else
            cecho alert "There was a problem creating the user, you should run as www user [1]"
        fi
    elif [[ $REPLY -eq 1 ]];then
        USER_NAME='www'
        GROUP_NAME='www'
        break
    fi
done

if [ -d "/Applications/Server.app" ]; then
    while true; do
        cread question "Will you be running on OS X Server [y/n]?" yesno
        if [[ $REPLY =~ ^[Yy]$ ]];then
            OSX_SERVER_INSTALL=true
            break
        elif [[ $REPLY =~ ^[Nn]$ ]];then
            OSX_SERVER_INSTALL=false
            break
        fi
    done 
fi

while true; do
    if [ "${OSX_SERVER_INSTALL}" == true ]; then
        cread question "Choose virtual environment path [${OSX_SERVER_SITES_DEFAULT}]:" REPLY_VIR_ENV
        if [ ! -z "${REPLY_VIR_ENV}" ]; then
            DJANGO_WEBAPP_VIR_ENV="${REPLY_VIR_ENV}"
        else
            DJANGO_WEBAPP_VIR_ENV="${OSX_SERVER_SITES_DEFAULT}"
        fi
    else
        cread notice "Choose virtual environment path: " DJANGO_WEBAPP_VIR_ENV
    fi
    
    #This will make sure there's a trailing slash on the path
    eval_dir DJANGO_WEBAPP_VIR_ENV
    
    if [ $? == 0 ]; then
        if [ -d  "${DJANGO_WEBAPP_VIR_ENV}" ]; then
            DJANGO_WEBAPP_VIR_ENV="${DJANGO_WEBAPP_VIR_ENV}${VIRENV_NAME}"
            eval_dir DJANGO_WEBAPP_VIR_ENV    
            cread question "  correct path:${DJANGO_WEBAPP_VIR_ENV} [y/n/c]? " yesno
            if [[ $REPLY =~ ^[Yy]$ ]];then
                    break
            elif [[ $REPLY =~ ^[Cc]$ ]];then
                cecho bold "Canceling..."
                exit 1
            fi 
        else
            cecho alert "That's not a valid path, please try again"
        fi
    else
        cecho alert "Please choose a POSIX Compatible Path (i.e no spaces!)"
    fi
done

while true; do
    cread question "Do you want to run on an apache subpath \"${APACHE_SUBPATH}\"? [y/n]" yesno
    if [[ $REPLY =~ ^[Yy]$ ]];then
        RUN_ON_SUBPATH=true
        break
    elif [[ $REPLY =~ ^[Nn]$ ]]; then
        RUN_ON_SUBPATH=false        
        break
    fi  
done

while true; do
    cread question "Would you like to run the site in DEBUG mode [y/n]? " yesno
    if [[ $REPLY =~ ^[Yy]$ ]] ; then
        RUN_IN_DEBUG=true
        break
    elif [[ $REPLY =~ ^[Nn]$ ]] ; then
        RUN_IN_DEBUG=false
        break
    fi  
done

HOST_NAME=$(scutil --get HostName)
while true; do
    cread question "Set Site HostName:[default: $HOST_NAME]? " TMP_HOST_NAME
    if [ ! -z "${TMP_HOST_NAME}" ]; then
        HOST_NAME="${TMP_HOST_NAME}"
    fi
    cread question "Is this Correct? ${HOST_NAME} [y/n]? " yesno
    if [[ $REPLY =~ ^[Yy]$ ]];then
        break
    fi 
done

START_WEBAPP_ON_DEFAULT=false
if [ "${USER_NAME}" == 'www' ]; then 
	while true; do
		cread question "Do you want to enable the webapp on the default sites ( *:80 and *:443 ) [y/n]? " yesno
	    if [[ $REPLY =~ ^[Yy]$ ]];then
			START_WEBAPP_ON_DEFAULT=true
	        break
	    elif [[ $REPLY =~ ^[Nn]$ ]] ; then
	        break
	    fi  
	done
fi
}

function install {
### Install the Vitrual Environment
    local VEV=$(which virtualenv)
    "${VEV}" "${DJANGO_WEBAPP_VIR_ENV}"
    
### Clone the Project into the New Virtual Environment
    PROJECT_PATH="${DJANGO_WEBAPP_VIR_ENV}/${PROJECT_NAME}"
    if [ ! -d "${PROJECT_PATH}/.git" ] ;then
        git clone -b "${GIT_BRANCH}" "${GIT_REPO}" "${DJANGO_WEBAPP_VIR_ENV}/${PROJECT_NAME}"
    else
        cecho red "The project already exists"
    fi

    cd "${DJANGO_WEBAPP_VIR_ENV}"

    source bin/activate
    if [ -f "${PROJECT_PATH}/${DJANGO_REQUIREMENTS_FILE}" ] ;then
        pip install -r "${PROJECT_PATH}/${DJANGO_REQUIREMENTS_FILE}"
    elif [ ${#DJANGO_PIP_REQUIREMENTS[@]} -gt 0 ]; then
        for i in "${DJANGO_REQUIREMENTS[@]}"; do
            pip install "${i}"
        done
    fi
    
    cd "${PROJECT_PATH}"
        
    configure_settings_file
    configure_site_fixture

    python ./manage.py collectstatic --noinput
    
## Initialize the DB and Subsequently Set Permissions
    python ./manage.py syncdb

    for i in "${SOUTH_MANAGED_DJANGO_APPS[@]}"; do
        if [ "$(find ./${i}/migrations/ | wc -l)"  -eq 0 ]; then
            python ./manage.py schemamigration ${i} --initial
        else
            python ./manage.py schemamigration ${i} --auto
        fi
        python ./manage.py migrate ${i}
    done    
 
## Perform any needed Custom Configuration 
    custom_configuration   
    
## Install OSX Server Components If needed
    if [ ${OSX_SERVER_INSTALL} == true ];then
        ised "RUNNING_ON_APACHE=" "RUNNING_ON_APACHE=True" "${SETTINGS_FILE}"
        install_osx_server_components
    else
        cread question "Do you Want to start the django test server now [y/n]?" yesno
        if [[ $REPLY =~ ^[Yy]$ ]];then
            python manage.py runserver
            echo ""
            cecho info "to run in the future you need do..."
            cecho bold "sudo -u ${USER_NAME} ${python ${DJANGO_WEBAPP_VIR_ENV}${PROJECT_NAME}/manage.py runserver}"
        fi
    fi
}

function configure_settings_file () {
    cecho blue "Configuring to the settings.py file"

    EXAMPLE_SETTINGS_FILE=$(find "${PROJECT_PATH}" -type f \( -iname "*settings*.py" ! -iname "settings.py" \) -print -quit)
    if [ "${EXAMPLE_SETTINGS_FILE}" == "" ] ; then
        cecho red "There was a problem locating the Settings template."
        cecho red "Cannot continue with out this, exiting..."
        exit
    fi

    SETTINGS_FILE=$(dirname "${EXAMPLE_SETTINGS_FILE}")/settings.py
    cp "${EXAMPLE_SETTINGS_FILE}" "${SETTINGS_FILE}"
   
    ## Generate A Unique Secret Key For Django Site
    local SECKEY=$(LC_CTYPE=C tr -dc A-Za-z0-9_\!\@\#\$\%\^\*\(\)-+= < /dev/urandom | head -c 50 | xargs)
    ised "SECRET_KEY" "SECRET_KEY = '${SECKEY}'" "${SETTINGS_FILE}"
     
    if [ "${RUN_ON_SUBPATH}" == true ]; then
        ised "APACHE_RUN_ON_SUBPATH=" "APACHE_RUN_ON_SUBPATH=True" "${SETTINGS_FILE}"
    else
        APACHE_SUBPATH=""
        ised "APACHE_RUN_ON_SUBPATH=" "APACHE_RUN_ON_SUBPATH=False" "${SETTINGS_FILE}"
    fi

    if [ "${OSX_SERVER_INSTALL}" == true ]; then
        ised "RUNNING_ON_APACHE=" "RUNNING_ON_APACHE=True" "${SETTINGS_FILE}"
    fi

    if [ "${RUN_IN_DEBUG}" == true ] ; then
        ised "DEBUG=" "DEBUG=True" "${SETTINGS_FILE}"
    fi

    if [ "${SET_ALLOWED_HOST}" == true ] ; then 
        ised "ALLOWED_HOSTS=" "ALLOWED_HOSTS=['${HOST_NAME}']" "${SETTINGS_FILE}"
    fi
}

function configure_site_fixture () {
SITE_FIXTURE="${PROJECT_PATH}/host_name_fixture.json"
cat <<EOF > "${SITE_FIXTURE}"
[
    {
        "pk": 1,
        "model": "sites.site",
        "fields": {
        "name": "${HOST_NAME}",
        "domain":"${HOST_NAME}"
        }
    }
]
EOF

python ./manage.py loaddata "${SITE_FIXTURE}"
# rm "${SITE_FIXTURE}"
}

function install_osx_server_components () {
    cecho bold "installing os x server items..."
    
    STATIC_ROOT=$(python ./manage.py diffsettings | grep STATIC_ROOT | awk '{print $3}'|sed s/[\'\"]//g)
    STATIC_URL=$(python ./manage.py diffsettings  | grep STATIC_URL  | awk '{print $3}'|sed s/[\'\"\/]//g)
    MEDIA_ROOT=$(python ./manage.py diffsettings  | grep MEDIA_ROOT  | awk '{print $3}'|sed s/[\'\"]//g)
    
    write_webapp
    
    write_apache_config
    
    ## copy and configure the .wsgi file
    [[ ! -d "${OSX_SERVER_WSGI_DIR}/" ]] && mkdir -p "${OSX_SERVER_WSGI_DIR}/"  
    # cp -p "${DJANGO_WEBAPP_VIR_ENV}/${PROJECT_NAME}/${OSX_CONF_FILE_DIR}/${WSGI_FILE}" "${OSX_SERVER_WSGI_DIR}/"
    write_wsgi

    local venv_str="VIR_ENV_DIR = \'${DJANGO_WEBAPP_VIR_ENV}\'"
    ised "VIR_ENV_DIR" "${venv_str}" "${OSX_SERVER_WSGI_DIR}/${WSGI_FILE}"

    cecho info "OS X server items installed. "
	if [ "${START_WEBAPP_ON_DEFAULT}" == true ]; then
		webappctl status "${OSX_WEBAPP_PLIST}"
	else
		cecho blue "To enable the webapp, Open Server.app, select the site, go to Advanced and enable the webapp."
	fi
}

function write_apache_config (){
    ## configure the .conf file
    cecho info "writing apache configuration file"

    local static_files_alias_str="Alias /${STATIC_URL}/ ${STATIC_ROOT}/"
    local daemonprocess_str="WSGIDaemonProcess ${USER_NAME} user=${USER_NAME} group=${GROUP_NAME}"
    local processgroup_str="WSGIProcessGroup ${GROUP_NAME}"
    local wsgiscript_str="WSGIScriptAlias /${APACHE_SUBPATH} ${OSX_SERVER_WSGI_DIR}/${PROJECT_NAME}.wsgi"
    
    if [ "${USER_NAME}" == "www" ]; then
        echo "${wsgiscript_str}" > "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        echo "${static_files_alias_str}" >> "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
    else
        cp -p "${DJANGO_WEBAPP_VIR_ENV}/${PROJECT_NAME}/${OSX_CONF_FILE_DIR}/${APACHE_CONFIG_FILE}" "${OSX_SERVER_APACHE_DIR}/"
        
        ised "WSGIScriptAlias" "${wsgiscript_str}" "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        ised "Alias" "${static_files_alias_str}" "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        ised "WSGIDaemonProcess" "${daemonprocess_str}" "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
        ised "WSGIProcessGroup" "${processgroup_str}" "${OSX_SERVER_APACHE_DIR}/${APACHE_CONFIG_FILE}"
    fi

    custom_apache_configuration
}

function write_webapp () {
    [[ ! -d "${OSX_SERVER_APACHE_DIR}/webapps/" ]] && mkdir -p "${OSX_SERVER_APACHE_DIR}/webapps/"
    # cp -p "${DJANGO_WEBAPP_VIR_ENV}/${PROJECT_NAME}/${OSX_CONF_FILE_DIR}/${OSX_WEBAPP_PLIST}" "${OSX_SERVER_APACHE_DIR}/webapps/" 

    local dwf="defaults write ${OSX_SERVER_APACHE_DIR}/webapps/$OSX_WEBAPP_PLIST"
    $dwf displayName "$PROJECT_NAME"
    $dwf name "$OSX_WEBAPP_PLIST"
    $dwf includeFiles -array "${OSX_SERVER_APACHE_DIR}/$APACHE_CONFIG_FILE"
    $dwf installationIndicatorFilePath "${OSX_SERVER_WSGI_DIR}/$WSGI_FILE"
    $dwf requiredModuleNames -array wsgi_module
}

function write_wsgi () {
cat <<EOF > "${OSX_SERVER_WSGI_DIR}/${WSGI_FILE}"
''' WSGI file created using autoinstall script '''
import os, sys
import site

#set the next line to your printer_portal environment
VIR_ENV_DIR = '${DJANGO_WEBAPP_VIR_ENV}'

# Use site to load the site-packages directory of our virtualenv
site.addsitedir(os.path.join(VIR_ENV_DIR, 'lib/python2.7/site-packages'))

# Make sure we have the virtualenv and the Django app itself added to our path
sys.path.append(VIR_ENV_DIR)
sys.path.append(os.path.join(VIR_ENV_DIR, '${PROJECT_NAME}'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '${PROJECT_SETTINGS_DIR}.settings')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

EOF
}

function clean_up () {
    ## Set Permissions
    cecho info "Setting owner and group on $(pwd)"
    chown -R "${USER_NAME}:${GROUP_NAME}" "${DJANGO_WEBAPP_VIR_ENV}" 
    cecho info "Setting permission on settings.py to 700"
    chmod 700 "${SETTINGS_FILE}"
    custom_clean_up
}


function make_user_and_group {
    cecho bold "Checking user and group..."
    local USER_EXISTS=$(dscl . list /Users | grep -c "${USER_NAME}")
    local GROUP_EXISTS=$(dscl . list /Groups | grep -c "${GROUP_NAME}")
    
    if [ "$USER_EXISTS" -eq 0 ]; then
        cecho bold "Creating user ${USER_NAME}..."
        
        USER_ID=$(check_ID Users UniqueID)
        dscl . create /Users/"${USER_NAME}"
        dscl . create /Users/"${USER_NAME}" passwd *
        dscl . create /Users/"${USER_NAME}" UniqueID "${USER_ID}"
    else
        cecho bold "User ${USER_NAME} already exists, skipping..."
    fi

    if [ "$GROUP_EXISTS" -eq 0 ]; then
        cecho bold "Creating user ${USER_NAME}..."
        GROUP_ID=$(check_ID Groups PrimaryGroupID)
        dseditgroup -o create -i "${GROUP_ID}" -n . "${GROUP_NAME}"
    else
        cecho bold "Group ${GROUP_NAME} already exists, skipping..."
        GROUP_ID=$(dscl . read /Groups/"${GROUP_NAME}" PrimaryGroupID)
    fi
    
    ### this is outside of the conditional statement 
    ### to correct any previously set GroupID
    dscl . create /Users/"${USER_NAME}" PrimaryGroupID "${GROUP_ID}"
}


############################# Requirement Checks ###########
function requirements_check () {
    git_check
    root_check "$@"
    virtualenv_check
    custom_precondition_check
}

function git_check () {
    if [ -z "$(which git)" ] ; then
        cecho alert "git is required to procede."
        if [ -x "/usr/bin/xcode-select" ] ; then
            cecho question "would you like to install the xcode developer cli tools [y/n]?" yesno
            if [[ $REPLY =~ ^[Yy]$ ]];then
                /usr/bin/xcode-select --install
                cread bold "press any key after the install process has completed"
            else
                cecho alert "You can install git by running 'xcode-select --install' in your terminal at any time"
                exit 1
            fi
        else
            cecho alert "You can download the installer from http://sourceforge.net/projects/git-osx-installer/files/latest/download." 
            exit 1
        fi
    fi
}

function root_check () {
    if [[ $EUID != 0 ]]; then
        cecho red "This script needs to run with elevated privileges, enter your password"
        sudo "$0" "$@"
        exit 1
    fi
}

function virtualenv_check () {
    VEV=$(which virtualenv)
    if [ -z "${VEV}" ] ; then
        cread alert "Python virtualenv must be installed.  Install Now using easy_install [y/n]? " yesno
        if [[ $REPLY =~ ^[Yy]$ ]];then
            easy_install virtualenv
            VEV=$(which virtualenv)
        else
            cecho alert "Cancelling webapp install script.  Re-run after virtualenv is installed."
            exit 1
        fi 
    fi
}

############################# Utility Functions ############
cecho(){    
    case "$1" in
        red|alert) local COLOR=$(printf "\\e[1;31m");;
        green|attention) local COLOR=$(printf "\\e[1;32m");;
        yellow|warn) local COLOR=$(printf "\\e[1;33m");;
        blue|question) local COLOR=$(printf "\\e[1;34m");;
        purple|info) local COLOR=$(printf "\\e[1;35m");;
        cyan|notice) local COLOR=$(printf "\\e[1;36m");;
        bold|prompt) local COLOR=$(printf "\\e[1;30m");;
        *) local COLOR=$(printf "\\e[0;30m");;
    esac
    
    if [ -z "${2}" ];then
        local MESSAGE="${1}"
    else
        local MESSAGE="${2}"
    fi

    local RESET=$(printf "\\e[0m")  
    echo "${COLOR}${MESSAGE}${RESET} ${3}"  
}

cread(){    
    case "$1" in
        red|alert) local COLOR=$(printf "\\e[1;31m");;
        green|attention) local COLOR=$(printf "\\e[1;32m");;
        yellow|warn) local COLOR=$(printf "\\e[1;33m");;
        blue|question) local COLOR=$(printf "\\e[1;34m");;
        purple|info) local COLOR=$(printf "\\e[1;35m");;
        cyan|notice) local COLOR=$(printf "\\e[1;36m");;
        bold|prompt) local COLOR=$(printf "\\e[1;30m");;
        *) local COLOR=$(printf "\\e[0;30m");;
    esac    
    
    local MESSAGE="${2}"
    local RESET=$(printf "\\e[0m")  
    if [ -z "${3}" ];then
        read -e -p "${COLOR}${MESSAGE}${RESET} "
    elif [ "${3}" == "yesno" ]; then
        read -e -p "${COLOR}${MESSAGE}${RESET} " -n 1 -r
    else
        read -e -p "${COLOR}${MESSAGE}${RESET} " VAR
        eval "$3"='$VAR'
    fi
}

check_ID(){
    # $1 is the dscl path and $2 is the Match
    local ID=$(/usr/bin/dscl . list /"$1" "$2" | awk '{print $2}'| grep '[4][0-9][0-9]'| sort| tail -1)
    [[ -n $ID ]] && ((ID++)) || ID=400
        
    while true; do
        local IDCK=$(/usr/bin/dscl . list /"$1" "$2" | awk '{print $2}'| grep -c ${ID})
        if [ "$IDCK" -eq 0 ]; then
            break
        else
            cecho alert "That %2 is in use"
            read -e -p "Please specify another (press c to cancel auto-install script):" ID
        fi
    done
    
    if [ "${ID}" == "c" ] ; then
        cecho alert "exiting script."
        exit 1
    fi
    echo "$ID"    
}

eval_dir(){  
# pass the name of the variable you want to eval
# so you would pass MYVAR rather than $MYVAR    
    eval local __myvar="${!1}" 2>/dev/null
    if [ $? == 0 ]; then    
        local __len=${#__myvar}-1
        if [ "${__myvar:$__len}" != "/" ]; then
          __myvar=$__myvar"/"
        fi
        eval "$1"="$__myvar"
    else
        return 1
    fi
}

ised(){
    # $1 is the match $2 is the replacement $3 is the file
    sed -i "" -e "s;^${1}.*;${2};" "${3}"
}
## End Utility Functions

###
__main__ () {
    ## check that
    requirements_check "$@"

    ## get info from the user
    prompt_for_settings

    ## install components 
    install

    ## do the clean up
    clean_up
}


__main__

exit 0