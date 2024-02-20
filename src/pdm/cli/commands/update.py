from __future__ import annotations

import argparse
from collections import defaultdict
from typing import TYPE_CHECKING

from pdm.cli.commands.base import BaseCommand
from pdm.cli.filters import GroupSelection
from pdm.cli.hooks import HookManager
from pdm.cli.options import (
    frozen_lockfile_option,
    groups_group,
    install_group,
    lockfile_option,
    prerelease_option,
    save_strategy_group,
    skip_option,
    unconstrained_option,
    update_strategy_group,
    venv_option,
)
from pdm.exceptions import PdmUsageError, ProjectError

if TYPE_CHECKING:
    from typing import Collection

    from pdm.models.requirements import Requirement
    from pdm.project import Project


class Command(BaseCommand):
    """Update package(s) in pyproject.toml"""

    arguments = (
        *BaseCommand.arguments,
        groups_group,
        install_group,
        lockfile_option,
        frozen_lockfile_option,
        save_strategy_group,
        update_strategy_group,
        prerelease_option,
        unconstrained_option,
        skip_option,
        venv_option,
    )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-t",
            "--top",
            action="store_true",
            help="Only update those listed in pyproject.toml",
        )
        parser.add_argument(
            "--dry-run",
            "--outdated",
            action="store_true",
            dest="dry_run",
            help="Show the difference only without modifying the lockfile content",
        )
        parser.add_argument(
            "--no-sync",
            dest="sync",
            default=True,
            action="store_false",
            help="Only update lock file but do not sync packages",
        )
        parser.add_argument("packages", nargs="*", help="If packages are given, only update them")
        parser.set_defaults(dev=None)

    def handle(self, project: Project, options: argparse.Namespace) -> None:
        self.do_update(
            project,
            selection=GroupSelection.from_options(project, options),
            save=options.save_strategy or project.config["strategy.save"],
            strategy=options.update_strategy or project.config["strategy.update"],
            unconstrained=options.unconstrained,
            top=options.top,
            dry_run=options.dry_run,
            packages=options.packages,
            sync=options.sync,
            no_editable=options.no_editable,
            no_self=options.no_self,
            prerelease=options.prerelease,
            fail_fast=options.fail_fast,
            hooks=HookManager(project, options.skip),
        )

    @staticmethod
    def do_update(
        project: Project,
        *,
        selection: GroupSelection,
        strategy: str = "reuse",
        save: str = "compatible",
        unconstrained: bool = False,
        top: bool = False,
        dry_run: bool = False,
        packages: Collection[str] = (),
        sync: bool = True,
        no_editable: bool = False,
        no_self: bool = False,
        prerelease: bool | None = None,
        fail_fast: bool = False,
        hooks: HookManager | None = None,
    ) -> None:
        """Update specified packages or all packages"""
        from itertools import chain

        from pdm.cli.actions import do_lock, do_sync
        from pdm.cli.utils import check_project_file, populate_requirement_names, save_version_specifiers
        from pdm.models.requirements import strip_extras
        from pdm.models.specifiers import get_specifier
        from pdm.utils import normalize_name

        from tests import covering 

        if not hooks:
            covering["do_update"][0] = True
            hooks = HookManager(project) #hooks or HookManager(project)
        else: 
            covering["do_update"][1] = True

        check_project_file(project)
        if len(packages) > 0 and (top or len(selection.groups) > 1 or not selection.default):
            covering["do_update"][2] = True
            raise PdmUsageError(
                "packages argument can't be used together with multiple -G or " "--no-default or --top."
            )
        else: 
            covering["do_update"][3] = True

        all_dependencies = project.all_dependencies
        updated_deps: dict[str, dict[str, Requirement]] = defaultdict(dict)
        locked_groups = project.lockfile.groups
        if not packages:
            covering["do_update"][4] = True
            if prerelease is not None:
                covering["do_update"][5] = True
                raise PdmUsageError("--prerelease/--stable must be used with packages given")
            else: 
                covering["do_update"][6] = True

            selection.validate()
            for group in selection:
                covering["do_update"][7] = True
                updated_deps[group] = all_dependencies[group]
        else:
            covering["do_update"][8] = True
            group = selection.one()
            if locked_groups and group not in locked_groups:
                covering["do_update"][9] = True
                raise ProjectError(f"Requested group not in lockfile: {group}")
            else: 
                covering["do_update"][10] = True
            dependencies = all_dependencies[group]
            for name in packages:
                covering["do_update"][11] = True
                l = []
                for k in dependencies:
                    covering["do_update"][12] = True
                    if normalize_name(strip_extras(k)[0]) == normalize_name(name):
                        covering["do_update"][13] = True
                        l.append(k)
                    else: 
                        covering["do_update"][14] = True
                matched_name = next(iter(l),None)
                #    (k for k in dependencies if normalize_name(strip_extras(k)[0]) == normalize_name(name)),
                #    None,
                #)
                if not matched_name:
                    covering["do_update"][15] = True
                    if selection.dev: 
                        covering["do_update"][16] = True
                        raise ProjectError(
                            f"[req]{name}[/] does not exist in [primary]{group}[/] "
                            f"dev-dependencies."
                        )
                    else: 
                        covering["do_update"][17] = True
                        raise ProjectError(
                            f"[req]{name}[/] does not exist in [primary]{group}[/] "
                            f"dependencies."
                        )
                else: 
                    covering["do_update"][18] = True
                dependencies[matched_name].prerelease = prerelease
                updated_deps[group][matched_name] = dependencies[matched_name]
            l = []
            for v in chain.from_iterable(updated_deps.values()):
                covering["do_update"][19] = True
                l.append(f"[req]{v}[/]")

            project.core.ui.echo(
                "Updating packages: {}.".format(
                    ", ".join(l) #f"[req]{v}[/]" for v in chain.from_iterable(updated_deps.values()))
                )
            )
        if unconstrained:
            covering["do_update"][20] = True
            for deps in updated_deps.values():
                covering["do_update"][21] = True
                for dep in deps.values():
                    covering["do_update"][22] = True
                    dep.specifier = get_specifier("")
        else: 
            covering["do_update"][23] = True
        
        reqs = [] 
        for g, deps in all_dependencies.items():
            covering["do_update"][24] = True
            for r in deps.values():   
                covering["do_update"][25] = True
                if locked_groups is None or g in locked_groups:
                    covering["do_update"][26] = True
                    reqs.append(r)
                else: 
                    covering["do_update"][27] = True

        #reqs = [
        #    r
        #    for g, deps in all_dependencies.items()
        #    for r in deps.values()
        #    if locked_groups is None or g in locked_groups
        #]
        # Since dry run is always true in the locking,
        # we need to emit the hook manually with the real dry_run value
        hooks.try_emit("pre_lock", requirements=reqs, dry_run=dry_run)
        with hooks.skipping("pre_lock", "post_lock"):
            covering["do_update"][28] = True
            resolved = do_lock(
                project,
                strategy,
                chain.from_iterable(updated_deps.values()),
                reqs,
                dry_run=True,
                hooks=hooks,
                groups=locked_groups,
            )
        hooks.try_emit("post_lock", resolution=resolved, dry_run=dry_run)
        for deps in updated_deps.values():
            covering["do_update"][29] = True
            populate_requirement_names(deps)
        if unconstrained:
            covering["do_update"][30] = True
            # Need to update version constraints
            save_version_specifiers(updated_deps, resolved, save)
        else: 
            covering["do_update"][31] = True
        if not dry_run:
            covering["do_update"][32] = True
            if unconstrained:
                covering["do_update"][33] = True
                for group, deps in updated_deps.items():
                    covering["do_update"][34] = True
                    if selection.dev:
                        covering["do_update"][35] = True
                        b = True 
                    else: 
                        covering["do_update"][36] = True
                        b = False 
                    project.add_dependencies(deps, group, b)
            else: 
                covering["do_update"][37] = True
            project.write_lockfile(project.lockfile._data, False)
        else: 
            covering["do_update"][38] = True
        if sync or dry_run:
            covering["do_update"][39] = True
            requirements = []
            for deps in updated_deps.values():
                covering["do_update"][40] = True
                for r in deps.values():
                    covering["do_update"][41] = True
                    requirements.append(r)
            if top:
                covering["do_update"][42] = True
                tracked_names = list(chain.from_iterable(updated_deps.values()))
            else: 
                covering["do_update"][43] = True
                tracked_names = None 
            if no_self or "default" not in selection:
                covering["do_update"][44] = True
                b = True 
            else:
                covering["do_update"][45] = True
                b = False 
            do_sync(
                project,
                selection=selection,
                clean=False,
                dry_run=dry_run,
                requirements=requirements, #[r for deps in updated_deps.values() for r in deps.values()],
                tracked_names=tracked_names, #list(chain.from_iterable(updated_deps.values())) if top else None,
                no_editable=no_editable,
                no_self=b, #no_self or "default" not in selection,
                fail_fast=fail_fast,
                hooks=hooks,
            )
        else: 
            covering["do_update"][46] = True

