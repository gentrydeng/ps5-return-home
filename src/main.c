/* SPDX-License-Identifier: BSD-2-Clause */
/* One system-home URI request using the foreground user. No app termination. */
#include <stdint.h>
#include <stddef.h>
#include <ps5/kernel.h>
#include <ps5/klog.h>

extern int sceKernelLoadStartModule(const char *, size_t, const void *,
                                  uint32_t, const void *, int *);
extern int sceUserServiceInitialize(const void *);
extern int sceUserServiceGetForegroundUser(int *);

typedef struct {
    uint32_t size;
    uint32_t user_id;
} LaunchParameters;

typedef int (*InitializeShellUi)(void);
typedef int (*LaunchUri)(const char *, LaunchParameters *);

int main(void)
{
    const char *prefix = "[return-home-uri 0.1.0]";
    int priority = 256;
    int result = sceUserServiceInitialize(&priority);
    klog_printf("%s user_service_init=0x%08x\n", prefix, (unsigned)result);

    int user_id = -1;
    result = sceUserServiceGetForegroundUser(&user_id);
    if (result != 0 || user_id == 0 || user_id == -1) {
        klog_printf("%s foreground_user_failed=0x%08x\n", prefix, (unsigned)result);
        return 1;
    }

    int module = sceKernelLoadStartModule(
        "/system_ex/common_ex/lib/libSceShellUIUtil.sprx", 0, NULL, 0, NULL, NULL);
    if (module < 0) {
        klog_printf("%s module_load_failed=0x%08x\n", prefix, (unsigned)module);
        return 1;
    }

    InitializeShellUi initialize = (InitializeShellUi)kernel_dynlib_dlsym(
        -1, (uint32_t)module, "sceShellUIUtilInitialize");
    LaunchUri launch = (LaunchUri)kernel_dynlib_dlsym(
        -1, (uint32_t)module, "sceShellUIUtilLaunchByUri");
    if (!initialize || !launch) {
        klog_printf("%s required_symbol_missing\n", prefix);
        return 1;
    }

    result = initialize();
    klog_printf("%s shell_ui_init=0x%08x\n", prefix, (unsigned)result);
    LaunchParameters parameters = {sizeof(parameters), (uint32_t)user_id};
    result = launch("pshomeui:navigateToHome?bootCondition=psButton", &parameters);
    klog_printf("%s home_uri_result=0x%08x\n", prefix, (unsigned)result);
    return result == 0 ? 0 : 1;
}
