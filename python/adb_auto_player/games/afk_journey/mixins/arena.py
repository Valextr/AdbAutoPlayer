"""Arena Mixin."""

import logging
from abc import ABC
from time import sleep

from adb_auto_player import Coordinates, CropRegions, GameTimeoutError
from adb_auto_player.games.afk_journey import AFKJourneyBase


class ArenaMixin(AFKJourneyBase, ABC):
    """Arena Mixin."""

    def run_arena(self) -> None:
        """Use Arena attempts."""
        self.start_up()

        try:
            self._enter_arena()
        except GameTimeoutError:
            return

        while not self.game_find_template_match("arena/no_attempts.png"):
            self._choose_opponent()
            self._battle()

        for _ in range(2):
            if not self._claim_free_attempt():
                break

            self._choose_opponent()
            self._battle()

        logging.info("Arena finished.")

    ############################## Helper Functions ##############################

    def _enter_arena(self) -> None:
        """Enter Arena."""
        logging.info("Entering Arena...")
        self._navigate_to_default_state()
        self.click(Coordinates(460, 1830))  # Battle Modes
        try:
            arena_mode: tuple[int, int] = self.wait_for_template(
                "arena/label.png",
                timeout_message="Failed to find Arena.",
                timeout=self.MIN_TIMEOUT,
            )
            self.click(Coordinates(*arena_mode))
            sleep(2)
        except GameTimeoutError as fail:
            logging.error(f"{fail} {self.LANG_ERROR}")
            raise

        logging.debug("Checking for weekly arena notices.")
        all(self._confirm_notices() for _ in range(2))

    def _confirm_notices(self) -> bool:
        """Close out weekly reward and weekly notice popups.

        Returns:
            bool: True if notices were closed, False otherwise.
        """
        try:
            _: tuple[str, int, int] = self.wait_for_any_template(
                templates=["arena/weekly_rewards.png", "arena/weekly_notice.png"],
                timeout=self.MIN_TIMEOUT,
                timeout_message="No notices found.",
            )
            self.click(Coordinates(380, 1890))
            sleep(4)

            return True
        except GameTimeoutError as fail:
            logging.debug(fail)
            pass

        return False

    def _choose_opponent(self) -> None:
        """Choose Arena opponent."""
        try:
            logging.debug("Start arena challenge.")
            _, x, y = self.wait_for_any_template(
                templates=["arena/challenge.png", "arena/continue.png"],
                timeout=self.FAST_TIMEOUT,
                timeout_message="Failed to start Arena runs.",
            )
            sleep(2)
            self.click(Coordinates(x, y))

            logging.debug("Choosing opponent.")
            opponent: tuple[int, int] = self.wait_for_template(
                template="arena/opponent.png",
                crop=CropRegions(right=0.6),  # Target weakest opponent.
                timeout=self.FAST_TIMEOUT,
                timeout_message="Failed to find Arena opponent.",
            )
            self.click(Coordinates(*opponent))
        except GameTimeoutError as fail:
            logging.error(fail)

    def _battle(self) -> None:
        """Battle Arena opponent."""
        try:
            logging.debug("Initiate battle.")
            start: tuple[int, int] = self.wait_for_template(
                template="arena/battle.png",
                timeout=self.FAST_TIMEOUT,
                timeout_message="Failed to start Arena battle.",
            )
            sleep(2)
            self.click(Coordinates(*start))

            logging.debug("Skip battle.")
            skip: tuple[int, int] = self.wait_for_template(
                template="arena/skip.png",
                timeout=self.MIN_TIMEOUT,
                timeout_message="Failed to skip Arena battle.",
            )
            self.click(Coordinates(*skip))

            logging.debug("Battle complete.")
            confirm: tuple[int, int] = self.wait_for_template(
                template="arena/done.png",
                timeout=self.MIN_TIMEOUT,
                timeout_message="Failed to confirm Arena battle completion.",
            )
            sleep(4)
            self.click(Coordinates(*confirm))
            sleep(2)
        except GameTimeoutError as fail:
            logging.error(fail)

    def _claim_free_attempt(self) -> bool:
        """Claim free Arena attempts.

        Returns:
            bool: True if free attempt claimed, False not available.
        """
        try:
            logging.debug("Claiming free attempts.")
            buy: tuple[int, int] = self.wait_for_template(
                template="arena/buy.png",
                timeout=self.FAST_TIMEOUT,
                timeout_message="Failed looking for free attempts.",
            )
            self.click(Coordinates(*buy))
        except GameTimeoutError:
            return True  # Not breaking, but would be interested in why it failed.

        try:
            _: tuple[int, int] = self.wait_for_template(
                template="arena/buy_free.png",
                timeout=self.FAST_TIMEOUT,
                timeout_message="No more free attempts.",
            )
            logging.debug("Free attempt found.")
        except GameTimeoutError as fail:
            logging.info(fail)
            cancel: tuple[int, int] | None = self.game_find_template_match(
                "arena/cancel_purchase.png"
            )
            (
                self.click(Coordinates(*cancel))
                if cancel
                else self.click(Coordinates(550, 1790))  # Cancel fallback
            )

            return False

        logging.debug("Purchasing free attempt.")
        self._click_confirm_on_popup()

        return True
