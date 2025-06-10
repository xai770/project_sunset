from typing import Any, Dict, List, Optional

class ModuleConfig:
    def __init__(
        self,
        models: Optional[List[str]] = None,
        conservative_bias: bool = False,
        **kwargs: Any
    ) -> None: ...
    
    models: Optional[List[str]]
    conservative_bias: bool
