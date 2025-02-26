using static Bullseye.Targets;
using static SimpleExec.Command;

const string RESTORE_TOOLS = "restore-tools";
const string BUILD_SERVER_VERSION = "build-server-version";

Target(
  RESTORE_TOOLS,
  () =>
  {
    Run("dotnet", "tool restore");
  }
);

Target(
  BUILD_SERVER_VERSION,
  DependsOn(RESTORE_TOOLS),
  () =>
  {
    Run("dotnet", "tool run dotnet-gitversion /output json /output buildserver");
  }
);


await RunTargetsAndExitAsync(args).ConfigureAwait(true);
