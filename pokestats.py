import json
from pathlib import Path
import sys
from typing import Any, Optional


class Datafile:
    """This class acts as an interface with the json data file"""

    # consts
    FUNC: str = "func"
    HELP: str = "help"
    PARAMS: str = "params"
    NAME: str = "name"
    TYPE: str = "type"

    EV: str = "ev"
    HA: str = "ha"

    def __init__(self, filepath):
        self.filepath = filepath
        self.data = self.load_data()
        self.ev_fields = ("HP", "Atk", "Def", "SpAtk", "SpDef", "Spd")

    @classmethod
    def functions(cls) -> dict:
        """Get a mapping over command-line options and class function"""

        return {
            cls.EV: {
                cls.FUNC: cls.print_ev_yield,
                cls.HELP: "Get the ev yield of a pokémon",
                cls.PARAMS: [
                    {
                        cls.NAME: "pokemon",
                        cls.TYPE: "str",
                        cls.HELP: "The pokémon to display ev yield for"
                    }
                ]
            },
            cls.HA: {
                cls.FUNC: cls.print_hidden_ability,
                cls.HELP: "Get the hidden ability of a pokémon",
                cls.PARAMS: [
                    {
                        cls.NAME: "pokemon",
                        cls.TYPE: "str",
                        cls.HELP: "The pokémon to display hidden ability for"
                    }
                ]
            }
        }

    @classmethod
    def option_help(cls, option: str) -> str:
        """Return a help message for a provided command-line option"""

        _option = cls.functions()[option]

        desc_indent = " " * 32
        param_indent = " " * 4

        output = f"\n  {option}".ljust(len(desc_indent))
        output += _option[cls.HELP]
        if _option.get(cls.PARAMS):
            for param in _option[cls.PARAMS]:
                output += f"\n{param_indent}[{param[cls.NAME]}: {param[cls.TYPE]}]".ljust(len(desc_indent))
                output += param[cls.HELP]

        return output

    @classmethod
    def help(cls) -> str:
        """Return a helpful help message for using this script"""

        output = f"Get pokémon data. Available options:\n"
        for option in cls.functions().keys():
            output += cls.option_help(option)

        return output

    def load_data(self) -> dict:
        """Load the json file"""

        json_data = None
        with open(self.filepath, 'r') as f:
            json_data = json.loads(f.readline())

        return json_data

    def get_dict(self, key: str, value: Any) -> Optional[dict]:
        """Return the first dict matching the provided value for the specified key"""

        lower = False
        if isinstance(value, str):
            lower = True

        for n, item in enumerate(self.data):
            i = item[key]
            if lower:
                i = i.lower()
            if i == value:
                return self.data[n]

        return None

    def ev_yield(self, pokemon: str) -> Optional[list]:
        """Get the EV yield for the specified pokémon"""

        pokemon_data = self.get_dict(key="name", value=pokemon.lower())
        return pokemon_data["ev_yield"] if pokemon_data else None

    def print_ev_yield(self, pokemon: str) -> str:
        """Output a string describing the EV yield of the input pokémon"""

        ev_yield = self.ev_yield(pokemon)
        if not ev_yield:
            return f"Pokémon {pokemon} not found"

        output = ""
        for n, ev in enumerate(ev_yield):
            if ev:
                if output != "":
                    output += ", "

                output += f"{self.ev_fields[n]}: {ev}"

        return output

    def hidden_ability(self, pokemon: str) -> Optional[str]:
        """Get the hidden ability of the specified pokémon, if any"""

        pokemon_data = self.get_dict(key="name", value=pokemon.lower())
        if not pokemon_data:
            # Could not find pokémon. Return None
            return None

        abilities = pokemon_data["abilities"]
        # The abilities are listed as ["ability1", "ability2", "hidden ability"]
        # If a pokémon does not have a secondary or hidden ability, the prior ability is repeated
        if abilities[2] != abilities[0] and abilities[2] != abilities[1]:
            return abilities[2]
        else:
            return "None"

    def print_hidden_ability(self, pokemon: str) -> str:
        """Output the hidden ability of the input pokémon, if any"""

        hidden_ability = self.hidden_ability(pokemon)
        if hidden_ability:
            return f"Hidden ability: {hidden_ability}"
        else:
            return f"Pokémon {pokemon} not found"


def handle_args() -> Optional[dict]:
    """Handle command-line arguments. Return function to call as dict with method, args and kwargs"""

    if len(sys.argv) <= 1:
        print(Datafile.help())
    else:
        arg = sys.argv[1].lower()
        if arg not in Datafile.functions().keys():
            print(f"Unknown option '{arg}'. Available options: {[key for key in Datafile.functions().keys()]}")
            return

        command_dict = Datafile.functions()[arg]
        command_params = sys.argv[2:]
        required_params = command_dict.get(Datafile.PARAMS)
        if len(command_params) != len(required_params):
            print(Datafile.option_help(arg))
            return

        args = []
        kwargs = {}
        for param in command_params:
            if '=' in param:
                items = param.split('=')
                kwargs[items[0]] = items[1]
            else:
                args.append(param)

        return {
            "call": command_dict[Datafile.FUNC],
            "args": args,
            "kwargs": kwargs
        }

    return


if __name__ == "__main__":
    command = handle_args()

    if command:
        POKEMON_JSON = Path(__file__).parent / "pokemon.json"
        datafile = Datafile(filepath=POKEMON_JSON)

        method = getattr(datafile, command["call"].__name__)
        print(method(*command["args"], **command["kwargs"]))
