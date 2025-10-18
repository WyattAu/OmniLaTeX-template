        def ansi_escaped_string( ¬\phnote{A random reference: \cref{fig:censorbox}}¬
            string: str,
            *,
            effects: Union[List[str], None] = None,
            foreground_color: Union[str, None] = None,
            background_color: Union[str, None] = None,
            bright_fg: bool = False,
            bright_bg: bool = False,
        ) -> str:
            """Provides a human-readable interface to escape strings for terminal output.
    
            Using ANSI escape characters, the appearance of terminal output can be changed. The
            escape chracters are numerical and impossible to remember. Also, they require
            special starting and ending sequences. This function makes accessing that easier.
    
            Args:
                string: The input string to be escaped and altered.
                effects: The different effects to apply, e.g. underlined.
                foreground_color: The foreground, that is text color.
                background_color: The background color (appears as a colored block).
                bright_fg: Toggle whatever color was given for the foreground to be bright.
                bright_bg: Toggle whatever color was given for the background to be bright.
    
            Returns:
                A string with requested ANSI escape characters inserted around the input string.
            """
    
            def pad_sgr_sequence(sgr_sequence: str = "") -> str:
                """Pads an SGR sequence with starting and end parts.
    
                To 'Select Graphic Rendition' (SGR) to set the appearance of the following
                terminal output, the CSI is called as:
                CSI n m
                So, 'm' is the character ending the sequence. 'n' is a string of parameters, see
                dict below.
    
                Args:
                    sgr_sequence: Sequence of SGR codes to be padded.
                Returns:
                    Padded SGR sequence.
                """
                control_sequence_introducer = "\x1B["  # hexadecimal '1B'
                select_graphic_rendition_end = "m"  # Ending character for SGR
                return control_sequence_introducer + sgr_sequence + select_graphic_rendition_end
    
            # Implement more as required, see
            # https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters.
            sgr_parameters = {
                "underlined": 4,
            }
    
            sgr_foregrounds = {  # Base hardcoded mapping, all others can be derived
                "black": 30,
                "red": 31,
                "green": 32,
                "yellow": 33,
                "blue": 34, ¬\phnum{\(30 + 4\)}¬
                "magenta": 35,
                "cyan": 36,
                "white": 37,
            }
    
            # These offsets convert foreground colors to background or bright color codes, see
            # https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
            bright_offset = 60
            background_offset = 10
    
            if bright_fg:
                sgr_foregrounds = {
                    color: value + bright_offset for color, value in sgr_foregrounds.items()
                }
    
            if bright_bg:
                background_offset += bright_offset
    
            sgr_backgrounds = {
                color: value + background_offset for color, value in sgr_foregrounds.items()
            }
    
            # Chain various parameters, e.g. 'ESC[30;47m' to get white on black, if 30 and 47
            # were requested. Note, no ending semicolon. Collect codes in a list first.
            sgr_sequence_elements: List[int] = []
    
            if effects is not None:
                for sgr_effect in effects:
                    try:
                        sgr_sequence_elements.append(sgr_parameters[sgr_effect])
                    except KeyError:
                        raise NotImplementedError(
                            f"Requested effect '{sgr_effect}' not available."
                        )
            if foreground_color is not None:
                try:
                    sgr_sequence_elements.append(sgr_foregrounds[foreground_color])
                except KeyError:
                    raise NotImplementedError(
                        f"Requested foreground color '{foreground_color}' not available."
                    )
            if background_color is not None:
                try:
                    sgr_sequence_elements.append(sgr_backgrounds[background_color])
                except KeyError:
                    raise NotImplementedError(
                        f"Requested background color '{background_color}' not available."
                    )
    
            # To .join() list, all elements need to be strings
            sgr_sequence: str = ";".join(str(sgr_code) for sgr_code in sgr_sequence_elements)
    
            reset_all_sgr = pad_sgr_sequence()  # Without parameters: reset all attributes
            sgr_start = pad_sgr_sequence(sgr_sequence)
            return sgr_start + string + reset_all_sgr
