
TAILWIND_VER="v3.4.17"
PREFIX="~/.local/bin"
EXE_NAME="tailwindcss"

install() {
    # its binnary executable for tailwind cli
    INSTALL_FROM="https://github.com/tailwindlabs/tailwindcss/releases/download/${TAILWIND_VER}/tailwindcss-linux-x64"
    echo $INSTALL_FROM
    TMP_LOC="~/tmp/${EXE_NAME}"
    mkdir $TMP_LOC
    echo $PREFIX
    curl --progress-bar -L $INSTALL_FROM -o $TMP_LOC
    # chmod 755 ${TMP_LOC}
    # cp $TMP_LOC $PREFIX/$EXE_NAME
}
