import re
from typing import List, Dict, Any

class AdvancedSearch:
    def __init__(self, data_source: List[Dict[str, Any]]):
        """Initialize with a list of data entries (e.g. documents, notes, etc.)"""
        self.data = data_source

    def _filter_by_fields(self, filters: Dict[str, Any], items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter items by given key-value filters"""
        if not filters:
            return items
        filtered = []
        for item in items:
            match = True
            for key, value in filters.items():
                if key not in item or str(item[key]).lower() != str(value).lower():
                    match = False
                    break
            if match:
                filtered.append(item)
        return filtered

    def _autocomplete(self, prefix: str, field: str = 'title', limit: int = 5) -> List[str]:
        """Return autocomplete suggestions for a given prefix on a field"""
        prefix = prefix.lower()
        suggestions = set()
        for item in self.data:
            if field in item:
                val = str(item[field])
                if val.lower().startswith(prefix):
                    suggestions.add(val)
                    if len(suggestions) >= limit:
                        break
        return list(suggestions)

    def _parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """Basic natural language query parsing to extract filters and keywords"""
        # Example: "find notes about AI from author John"
        # Extremely simplistic parsing for demo purposes
        filters = {}
        keywords = []

        # Regex for from author <name>
        author_match = re.search(r'from author ([\w ]+)', query, re.IGNORECASE)
        if author_match:
            filters['author'] = author_match.group(1).strip()
            query = query.replace(author_match.group(0), '')

        # Regex for in category <cat>
        category_match = re.search(r'in category ([\w ]+)', query, re.IGNORECASE)
        if category_match:
            filters['category'] = category_match.group(1).strip()
            query = query.replace(category_match.group(0), '')

        # Remove common words
        cleaned_query = re.sub(r'\b(find|search|notes|about|with|and|the|a|an)\b', '', query, flags=re.IGNORECASE)
        cleaned_query = cleaned_query.strip()

        if cleaned_query:
            keywords = cleaned_query.split()

        return {'filters': filters, 'keywords': keywords}

    def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Perform a search over the data.
        Supports natural language queries and explicit filters.

        :param query: search query string, can be natural language
        :param filters: explicit filters as dict
        :return: list of matched items
        """
        parsed = self._parse_natural_language_query(query)
        combined_filters = filters or {}
        combined_filters.update(parsed.get('filters', {}))

        # Filter data first
        filtered_data = self._filter_by_fields(combined_filters, self.data)

        # If there are keywords, filter by them (simple substring match in 'content' or 'title')
        keywords = parsed.get('keywords', [])
        if keywords:
            result = []
            for item in filtered_data:
                searchable_text = ((item.get('title', '') + ' ' + item.get('content', ''))).lower()
                if all(kw.lower() in searchable_text for kw in keywords):
                    result.append(item)
            return result
        else:
            return filtered_data

    def autocomplete(self, prefix: str, field: str = 'title', limit: int = 5) -> List[str]:
        """Get autocomplete suggestions"""
        return self._autocomplete(prefix, field, limit)
