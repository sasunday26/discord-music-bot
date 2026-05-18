from lavalink.abc import Filter


class Echo(Filter):
    def __init__(self) -> None:
        super().__init__(
            {"echoLength": 0.1, "decay": 0.4},
            plugin_filter=True,
        )

    def update(self, **kwargs) -> None:
        if "echo_length" in kwargs:
            self.values["echoLength"] = float(kwargs["echo_length"])
        if "decay" in kwargs:
            self.values["decay"] = float(kwargs["decay"])

    def serialize(self) -> dict:
        return {"echo": dict(self.values)}


class LowPassPlugin(Filter):
    def __init__(self) -> None:
        super().__init__(
            {"cutoffFrequency": 1500, "boostFactor": 1.0},
            plugin_filter=True,
        )

    def update(self, **kwargs) -> None:
        if "cutoff_frequency" in kwargs:
            self.values["cutoffFrequency"] = int(kwargs["cutoff_frequency"])
        if "boost_factor" in kwargs:
            self.values["boostFactor"] = float(kwargs["boost_factor"])

    def serialize(self) -> dict:
        return {"low-pass": dict(self.values)}
