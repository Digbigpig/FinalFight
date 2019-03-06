from discord.ext.commands import UserInputError


class DataIntegrity(UserInputError):
    """
    Exception raised when a data integrity violations are attempted through user input.
    """
    pass


class DataCurrentlyExists(DataIntegrity):
    """
    Exception raised when attempting to insert data that currently exists
    in the database.
    """


class DataDoesNotExists(DataIntegrity):
    """
    Exception raised when attempting to delete data that doesn't currently exists
    in the database.
    """


class DataCreated(DataIntegrity):
    """
    Exception raised when the necessary data did not exist but was created.
    """


class GameIntegrity(UserInputError):
    """
    Exception raised when the necessary data did not exist but was created.
    """


class NotUserTurn(GameIntegrity):
    """
    Exception raised when the necessary data did not exist but was created.
    """


class RuleViolation(GameIntegrity):
    """
    Exception raised when the necessary data did not exist but was created.
    """


class InsufficientSpecial(GameIntegrity):
    """
    todo
    """


class PlayerFrozen(GameIntegrity):
    """
    todo
    """