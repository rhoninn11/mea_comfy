

GO_VER="1.26.3"
install() {
    PKG="go${GO_VER}.linux-amd64.tar.gz"
    INSTALL_FROM="https://go.dev/dl/${PKG}"
    TMP_LOC="/tmp/${PKG}"
    PREFIX="/usr/local"
    curl --progress-bar -L $INSTALL_FROM -o $TMP_LOC
    tar --directory=${PREFIX} -xzf $TMP_LOC
    echo 'export PATH="$PATH:'$PREFIX'/go/bin"' > /etc/profile.d/go.sh
    rm $TMP_LOC
}