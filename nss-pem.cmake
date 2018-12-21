# Add external nss header locations
include_directories(../../dist/public/nss;../../dist/private/nss)
# Find the external library path for linking
execute_process(COMMAND find ${PROJECT_SOURCE_DIR}/../../dist -name libnssckfw.a OUTPUT_VARIABLE NSS_EXT_LIB_PATH)
get_filename_component(NSS_LIB_PATH ${NSS_EXT_LIB_PATH} DIRECTORY)
link_directories(${NSS_LIB_PATH})
