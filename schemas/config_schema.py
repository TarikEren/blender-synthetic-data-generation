"""
Schema for the config file.
"""

config_schema = {
    "type": "object",
    "properties": {
        "scene": {
            "type": "object",
            "properties": {
                "name": { "type": "string" },
                "resolution": {
                    "type": "object",
                    "properties": {
                        "x": { "type": "integer" },
                        "y": { "type": "integer" },
                        "percentage": { "type": "number" }
                    },
                    "required": ["x", "y", "percentage"]
                },
                "camera": {
                    "type": "object",
                    "properties": {
                        "position": {
                            "type": "object",
                            "properties": {
                                "x": { "type": "number" },
                                "y": { "type": "number" },
                                "z": { "type": "number" }
                            },
                             "required": ["x", "y", "z"]
                        },
                         "rotation": {
                            "type": "object",
                            "properties": {
                                "x": { "type": "number" },
                                "y": { "type": "number" },
                                "z": { "type": "number" }
                            },
                             "required": ["x", "y", "z"]
                        }
                    },
                    "required": ["position", "rotation"]
                },
                "light": {
                    "type": "object",
                    "properties": {
                         "position": {
                            "type": "object",
                            "properties": {
                                "x": { "type": "number" },
                                "y": { "type": "number" },
                                "z": { "type": "number" }
                            },
                             "required": ["x", "y", "z"]
                        },
                         "rotation": {
                            "type": "object",
                            "properties": {
                                "x": { "type": "number" },
                                "y": { "type": "number" },
                                "z": { "type": "number" }
                            },
                             "required": ["x", "y", "z"]
                        }
                    },
                    "required": ["position", "rotation"]
                },
                 "engine": { "type": "string" },
                 "cycles": {
                     "type": "object",
                     "properties": {
                         "use_progressive_refine": { "type": "boolean" },
                         "tile_size": { "type": "integer" },
                         "use_persistent_data": { "type": "boolean" },
                         "samples": { "type": "integer" },
                         "use_adaptive_sampling": { "type": "boolean" },
                         "adaptive_threshold": { "type": "number" },
                         "use_denoising": { "type": "boolean" },
                         "max_bounces": { "type": "integer" },
                         "diffuse_bounces": { "type": "integer" },
                         "glossy_bounces": { "type": "integer" },
                         "sample_clamp_indirect": { "type": "number" }
                     },
                     "required": [
                         "use_progressive_refine",
                         "tile_size",
                         "use_persistent_data",
                         "samples",
                         "use_adaptive_sampling",
                         "adaptive_threshold",
                         "use_denoising",
                         "max_bounces",
                         "diffuse_bounces",
                         "glossy_bounces",
                         "sample_clamp_indirect"
                     ]
                 }
            },
            "required": ["name", "resolution", "camera", "light", "engine", "cycles"]
        },
        "paths": {
            "type": "object",
            "properties": {
                "models": { "type": "string" },
                "images": { "type": "string" },
                "labels": { "type": "string" },
                "vis": { "type": "string" },
                "textures": { "type": "string" }
            },
             "required": ["models", "images", "labels", "vis", "textures"]
        },
         "output": {
             "type": "object"
         },
        "create_visualization": { "type": "boolean" }
    },
    "required": ["scene", "paths", "output", "create_visualization"]
}