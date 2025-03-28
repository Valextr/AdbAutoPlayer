"""AFK Journey Dura's Trials Mixin."""

import logging
from abc import ABC
from time import sleep

from adb_auto_player import Coordinates, CropRegions
from adb_auto_player.games.afk_journey import AFKJourneyBase


class DurasTrialsMixin(AFKJourneyBase, ABC):
    """Dura's Trials Mixin."""

    def push_duras_trials(self) -> None:
        """Push Dura's Trials."""
        self.start_up()
        self.store[self.STORE_MODE] = self.MODE_DURAS_TRIALS
        self._navigate_to_duras_trials_screen()

        self.wait_for_template(
            template="duras_trials/rate_up.png",
            grayscale=True,
            crop=CropRegions(top=0.6, bottom=0.2),
        )
        sleep(0.5)
        rate_up_banners = self.find_all_template_matches(
            template="duras_trials/rate_up.png",
            grayscale=True,
            crop=CropRegions(top=0.6, bottom=0.2),
        )

        if not rate_up_banners:
            logging.warning(
                "Dura's Trials Rate Up banners could not be found, Stopping"
            )
            return None

        first_banner = True
        for banner in rate_up_banners:
            if not first_banner:
                self._navigate_to_duras_trials_screen()
            self._handle_dura_screen(*banner)
            self._navigate_to_duras_trials_screen()
            self._handle_dura_screen(*banner, nightmare_mode=True)
            first_banner = False

        return None

    def _navigate_to_duras_trials_screen(self) -> None:
        logging.info("Navigating to Dura's Trial select")

        def check_for_duras_trials_label() -> bool:
            match = self.game_find_template_match(
                template="duras_trials/featured_heroes.png",
                crop=CropRegions(left=0.7, bottom=0.8),
            )
            return match is not None

        self._navigate_to_default_state(check_callable=check_for_duras_trials_label)

        featured_heroes = self.game_find_template_match(
            template="duras_trials/featured_heroes.png",
            crop=CropRegions(left=0.7, bottom=0.8),
        )
        if featured_heroes is not None:
            return

        logging.info("Clicking Battle Modes button")
        self.click(Coordinates(x=460, y=1830), scale=True)
        duras_trials_label = self.wait_for_template(template="duras_trials/label.png")
        self.click(Coordinates(*duras_trials_label))
        self.wait_for_template(
            template="duras_trials/featured_heroes.png",
            crop=CropRegions(left=0.7, bottom=0.8),
        )
        return None

    def _dura_resolve_state(self) -> tuple[str, int, int]:
        while True:
            template, x, y = self.wait_for_any_template(
                templates=[
                    "battle/records.png",
                    "duras_trials/battle.png",
                    "duras_trials/sweep.png",
                    "guide/close.png",
                    "guide/next.png",
                    "duras_trials/continue_gray.png",
                ],
            )

            match template:
                case "guide/close.png" | "guide/next.png":
                    self._handle_guide_popup()
                case _:
                    break
        return template, x, y

    def _handle_dura_screen(  # noqa: PLR0915 - TODO: Refactor better
        self, x: int, y: int, nightmare_mode: bool = False
    ) -> None:
        # y+100 clicks closer to center of the button instead of rate up text
        offset = int(self.get_scale_factor() * 100)
        self.click(Coordinates(x, y + offset))
        count = 0

        def handle_nightmare_pre_battle() -> bool:
            """Handle pre battle steps in nightmare mode.

            Returns:
                True to continue; False to abort.
            """
            # Get current state; if we already see records, skip nightmare handling.
            template, _, _ = self._dura_resolve_state()

            if template == "duras_trials/continue_gray.png":
                return False
            if template == "battle/records.png":
                return True

            nightmare = self.game_find_template_match(
                template="duras_trials/nightmare.png",
                crop=CropRegions(left=0.6, top=0.9),
            )
            if nightmare is None:
                logging.warning("Nightmare Button not found")
                return False
            self.click(Coordinates(*nightmare))

            template, new_x, new_y = self.wait_for_any_template(
                templates=[
                    "duras_trials/nightmare_skip.png",
                    "duras_trials/nightmare_swords.png",
                    "duras_trials/cleared.png",
                ],
                crop=CropRegions(top=0.7, bottom=0.1),
            )
            match template:
                case "duras_trials/nightmare_skip.png":
                    self.click(Coordinates(new_x, new_y))
                    self.wait_until_template_disappears(
                        "duras_trials/nightmare_skip.png",
                        crop=CropRegions(top=0.7, bottom=0.1),
                    )
                    self.click(Coordinates(new_x, new_y))
                    self.wait_for_template(
                        "duras_trials/nightmare_swords.png",
                        crop=CropRegions(top=0.7, bottom=0.1),
                    )
                    self.click(Coordinates(new_x, new_y))
                case "duras_trials/nightmare_swords.png":
                    self.click(Coordinates(new_x, new_y))
                case "duras_trials/cleared.png":
                    logging.info("Nightmare Trial already cleared")
                    return False
            return True

        def handle_non_nightmare_pre_battle() -> bool:
            """Handle pre battle steps in normal mode.

            Returns:
                True to continue; False to abort.
            """
            template, new_x, new_y = self._dura_resolve_state()
            match template:
                case "duras_trials/sweep.png":
                    logging.info("Dura's Trial already cleared")
                    return False
                case "duras_trials/battle.png":
                    self.click(Coordinates(new_x, new_y))
                case "battle/records.png":
                    # No action needed.
                    pass
            return True

        def handle_non_nightmare_post_battle() -> bool:
            """Handle post battle actions for normal mode.

            Returns:
                True if the trial is complete, or False to continue pushing battles.
            """
            self.wait_for_template(
                template="duras_trials/first_clear.png",
                crop=CropRegions(left=0.3, right=0.3, top=0.6, bottom=0.3),
            )
            next_button = self.game_find_template_match(
                template="next.png", crop=CropRegions(left=0.6, top=0.9)
            )
            if next_button is not None:
                nonlocal count
                count += 1
                logging.info(f"Trials pushed: {count}")
                self.click(Coordinates(*next_button))
                self.click(Coordinates(*next_button))
                sleep(3)
                return False  # Continue battle loop
            else:
                logging.info("Dura's Trial completed")
                return True  # End loop

        def handle_nightmare_post_battle() -> bool:
            """Handle post battle actions for nightmare mode.

            Returns:
            True if the trial is complete, or False to continue.
            """
            nonlocal count
            count += 1
            logging.info(f"Nightmare Trials pushed: {count}")
            if self.game_find_template_match(
                template="duras_trials/continue_gray.png", crop=CropRegions(top=0.8)
            ):
                logging.info("Nightmare Trial completed")
                return True
            return False

        while True:
            # Pre battle handling based on mode.
            if nightmare_mode:
                if not handle_nightmare_pre_battle():
                    return
            elif not handle_non_nightmare_pre_battle():
                return

            # Handle the battle screen.
            result = self._handle_battle_screen(
                self.get_config().duras_trials.use_suggested_formations
            )

            if result is True:
                if nightmare_mode:
                    if handle_nightmare_post_battle():
                        return
                    # Else continue to the next loop iteration.
                elif handle_non_nightmare_post_battle():
                    return
                # Else continue to the next loop iteration.
            else:
                logging.info("Dura's Trial failed")
                return
