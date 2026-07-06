
PROTOC_VER="31.0"
    PREFIX="/usr/share/protoc"
install() {
    # INSTALL_FROM="https://github.com/protocolbuffers/protobuf/releases/download/v31.0/protoc-31.0-linux-x86_64.zip"
    INSTALL_FROM="https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VER}/protoc-${PROTOC_VER}-linux-x86_64.zip"
    echo $INSTALL_FROM
    TMP_LOC="~/tmp/protoc.zip"
    curl --progress-bar -L $INSTALL_FROM -o $TMP_LOC
    # unzip /tmp/protoc.zip -d $PREFIX
    # sudo cp $TMP_LOC $PREFIX/$EXE_NAME
    # prefix present in PATH by default
}
