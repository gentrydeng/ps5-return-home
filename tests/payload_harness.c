/* SPDX-License-Identifier: BSD-2-Clause */
/* Host mocks test control flow, not PS5 API compatibility or UI behavior. */
#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

int payload_main(void);
static const char *scenario;
static int launches, loads, initialized;
typedef struct { uint32_t size, user_id; } Parameters;

int klog_printf(const char *format, ...) { (void)format; return 0; }
int sceUserServiceInitialize(const void *arg)
{
    assert(arg && *(const int *)arg == 256);
    return strcmp(scenario, "already-initialized") == 0 ? -1 : 0;
}
int sceUserServiceGetForegroundUser(int *user)
{
    *user = 42;
    if (strcmp(scenario, "no-user") == 0) *user = -1;
    if (strcmp(scenario, "zero-user") == 0) *user = 0;
    return strcmp(scenario, "user-error") == 0 ? -1 : 0;
}
int sceKernelLoadStartModule(const char *name, size_t size, const void *arg,
                             uint32_t flags, const void *options, int *result)
{
    assert(strcmp(name, "/system_ex/common_ex/lib/libSceShellUIUtil.sprx") == 0);
    assert(!size && !arg && !flags && !options && !result);
    loads++;
    return strcmp(scenario, "module-error") == 0 ? -1 : 7;
}
static int initialize(void) { initialized++; return 0; }
static int launch(const char *uri, Parameters *parameters)
{
    assert(initialized == 1 && parameters->size == sizeof(Parameters));
    assert(parameters->user_id == 42);
    assert(strcmp(uri, "pshomeui:navigateToHome?bootCondition=psButton") == 0);
    launches++;
    return strcmp(scenario, "launch-error") == 0 ? -1 : 0;
}
uintptr_t kernel_dynlib_dlsym(int pid, uint32_t module, const char *name)
{
    assert(pid == -1 && module == 7);
    if (strcmp(name, "sceShellUIUtilInitialize") == 0)
        return strcmp(scenario, "missing-initialize") == 0 ? 0 : (uintptr_t)&initialize;
    assert(strcmp(name, "sceShellUIUtilLaunchByUri") == 0);
    return strcmp(scenario, "missing-launch") == 0 ? 0 : (uintptr_t)&launch;
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    scenario = argv[1];
    int result = payload_main();
    int user_failure = strcmp(scenario, "no-user") == 0 || strcmp(scenario, "zero-user") == 0
                       || strcmp(scenario, "user-error") == 0;
    int early_failure = user_failure || strcmp(scenario, "module-error") == 0
                        || strcmp(scenario, "missing-initialize") == 0
                        || strcmp(scenario, "missing-launch") == 0;
    int launch_failure = strcmp(scenario, "launch-error") == 0;
    assert(loads == (user_failure ? 0 : 1));
    assert(launches == (early_failure ? 0 : 1));
    assert(result == ((early_failure || launch_failure) ? 1 : 0));
    puts("PASS");
    return 0;
}
