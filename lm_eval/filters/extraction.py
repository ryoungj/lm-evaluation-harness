import re

from lm_eval.api.filter import Filter


class RegexFilter(Filter):
    """ """

    def __init__(
        self,
        regex_pattern: str = r"#### (\-?[0-9\.\,]+)",
        group_select=0,
        fallback: str = "[invalid]",
    ) -> None:
        """
        pass a string `regex` to run `re.compile(r"regex")` on.
        `fallback` defines the output returned if no matches for the regex are located.
        """
        self.regex_pattern = regex_pattern
        self.regex = re.compile(regex_pattern)
        self.group_select = group_select
        self.fallback = fallback

    def apply(self, resps, docs):
        # here, we assume we have a list, in which each element is
        # a list of model responses for some particular input/target pair.
        # so we process each of these (same input/target response sets)
        # independently (and keep them a list.)
        def filter_set(inst):
            filtered = []
            for resp in inst:
                match = self.regex.findall(resp)
                if match:
                    match = match[self.group_select]
                    if isinstance(match, tuple):
                        # Filter out empty strings and check if the resulting list is not empty
                        filtered_match = [m for m in match if m]
                        if filtered_match:
                            match = filtered_match[0]
                        else:
                            # Handle the case where the list is empty
                            match = None  # Or your preferred fallback value
                    match = match.strip() if match else self.fallback
                else:
                    match = self.fallback
                filtered.append(match)
            return filtered


        # print(resps)
        filtered_resps = list(map(lambda x: filter_set(x), resps))
        # print(filtered_resps)

        return filtered_resps


class WhitespaceFilter(Filter):
    """ """

    def __init__(self) -> None:
        pass

    def apply(self, resps, docs):
        def filter_set(inst):
            filtered_resp = []
            for resp in inst:
                if resp.startswith(" "):
                    resp = resp[1:]

                filtered_resp.append(resp)

            return filtered_resp

        filtered_resps = [filter_set(resp) for resp in resps]

        return filtered_resps
