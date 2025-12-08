"""Project-level analysis module (V8).

This module provides cross-file analysis capabilities including:
- Duplicate code detection using AST hashing
- Code similarity analysis
- Architecture recommendations
"""

import ast
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict


@dataclass
class FunctionSignature:
    """Signature and metadata for a function."""
    file: str
    name: str
    start_line: int
    end_line: int
    parameters: List[str]
    body_hash: str
    parameter_count: int
    line_count: int
    
    @property
    def location(self) -> str:
        return f"{self.file}:{self.start_line}-{self.end_line}"
    
    @property
    def qualified_name(self) -> str:
        return f"{Path(self.file).stem}.{self.name}"


@dataclass
class DuplicateGroup:
    """A group of similar/duplicate functions."""
    functions: List[FunctionSignature]
    similarity: float
    suggested_name: str = ""
    suggested_module: str = ""
    
    @property
    def count(self) -> int:
        return len(self.functions)
    
    @property
    def files(self) -> Set[str]:
        return {f.file for f in self.functions}
    
    @property
    def total_lines(self) -> int:
        return sum(f.line_count for f in self.functions)
    
    @property
    def potential_savings(self) -> int:
        """Lines that could be saved by consolidating."""
        if self.count <= 1:
            return 0
        avg_lines = self.total_lines // self.count
        return self.total_lines - avg_lines


@dataclass
class ProjectAnalysis:
    """Result of project-level analysis."""
    root_path: str
    files_analyzed: int = 0
    functions_found: int = 0
    duplicates: List[DuplicateGroup] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def duplicate_count(self) -> int:
        return sum(g.count for g in self.duplicates)
    
    @property
    def potential_savings(self) -> int:
        return sum(g.potential_savings for g in self.duplicates)


class ASTNormalizer(ast.NodeTransformer):
    """Normalize AST for comparison by renaming variables and stripping docstrings."""
    
    def __init__(self):
        self.name_map = {}
        self.counter = 0
        self.string_counter = 0
    
    def _get_normalized_name(self, original: str) -> str:
        if original not in self.name_map:
            self.name_map[original] = f"var_{self.counter}"
            self.counter += 1
        return self.name_map[original]
    
    def visit_Name(self, node):
        # Normalize variable names
        node.id = self._get_normalized_name(node.id)
        return node
    
    def visit_arg(self, node):
        # Normalize argument names
        node.arg = self._get_normalized_name(node.arg)
        return node
    
    def visit_FunctionDef(self, node):
        # Normalize function name
        node.name = "normalized_func"
        # Strip docstring if present
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]  # Remove docstring
        self.generic_visit(node)
        return node
    
    def visit_AsyncFunctionDef(self, node):
        # Same for async functions
        node.name = "normalized_func"
        # Strip docstring if present
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            node.body = node.body[1:]  # Remove docstring
        self.generic_visit(node)
        return node
    
    def visit_Constant(self, node):
        # Normalize string constants to detect structural similarity
        if isinstance(node.value, str):
            node.value = "str_const"
        return node


def normalize_ast(node: ast.AST) -> str:
    """Normalize an AST node for comparison.
    
    Removes variable names, function names, and other identifiers
    to compare structure only.
    
    Args:
        node: AST node to normalize
        
    Returns:
        String representation of normalized AST
    """
    import copy
    node_copy = copy.deepcopy(node)
    normalizer = ASTNormalizer()
    normalized = normalizer.visit(node_copy)
    return ast.dump(normalized, annotate_fields=False)


def hash_function_body(func_node: ast.FunctionDef) -> str:
    """Generate a hash of a function's body structure.
    
    Args:
        func_node: Function definition AST node
        
    Returns:
        MD5 hash of normalized function body
    """
    normalized = normalize_ast(func_node)
    return hashlib.md5(normalized.encode()).hexdigest()


def extract_functions_from_file(file_path: str) -> List[FunctionSignature]:
    """Extract all functions from a Python file.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        List of FunctionSignature objects
    """
    functions = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get parameter names
                params = []
                for arg in node.args.args:
                    params.append(arg.arg)
                
                # Calculate line count
                line_count = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                
                # Generate body hash
                body_hash = hash_function_body(node)
                
                sig = FunctionSignature(
                    file=file_path,
                    name=node.name,
                    start_line=node.lineno,
                    end_line=getattr(node, 'end_lineno', node.lineno),
                    parameters=params,
                    body_hash=body_hash,
                    parameter_count=len(params),
                    line_count=line_count,
                )
                functions.append(sig)
                
    except Exception as e:
        # Skip files that can't be parsed
        pass
    
    return functions


def calculate_similarity(hash1: str, hash2: str) -> float:
    """Calculate similarity between two hashes.
    
    For now, this is binary (1.0 if equal, 0.0 if not).
    Future: implement Levenshtein distance on normalized AST.
    
    Args:
        hash1: First hash
        hash2: Second hash
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    return 1.0 if hash1 == hash2 else 0.0


def find_duplicates(
    functions: List[FunctionSignature],
    threshold: float = 0.8,
    min_lines: int = 5,
) -> List[DuplicateGroup]:
    """Find duplicate/similar functions.
    
    Args:
        functions: List of function signatures
        threshold: Minimum similarity threshold (0.0-1.0)
        min_lines: Minimum function line count to consider
        
    Returns:
        List of DuplicateGroup objects
    """
    # Filter by minimum line count
    candidates = [f for f in functions if f.line_count >= min_lines]
    
    # Group by hash for exact duplicates
    hash_groups: Dict[str, List[FunctionSignature]] = defaultdict(list)
    for func in candidates:
        hash_groups[func.body_hash].append(func)
    
    # Find groups with duplicates
    duplicates = []
    for body_hash, group in hash_groups.items():
        if len(group) >= 2:
            # Suggest a consolidated name
            common_words = _find_common_words([f.name for f in group])
            suggested_name = common_words[0] if common_words else group[0].name
            
            # Suggest a module
            suggested_module = _suggest_module(group)
            
            dup_group = DuplicateGroup(
                functions=group,
                similarity=1.0,  # Exact match
                suggested_name=suggested_name,
                suggested_module=suggested_module,
            )
            duplicates.append(dup_group)
    
    # Sort by number of duplicates (most first)
    duplicates.sort(key=lambda g: g.count, reverse=True)
    
    return duplicates


def _find_common_words(names: List[str]) -> List[str]:
    """Find common words across function names."""
    if not names:
        return []
    
    # Split into words
    word_sets = []
    for name in names:
        # Split on underscores and camelCase
        words = set()
        current = []
        for char in name:
            if char == '_':
                if current:
                    words.add(''.join(current).lower())
                    current = []
            elif char.isupper() and current:
                words.add(''.join(current).lower())
                current = [char.lower()]
            else:
                current.append(char.lower())
        if current:
            words.add(''.join(current).lower())
        word_sets.append(words)
    
    # Find intersection
    if word_sets:
        common = word_sets[0]
        for ws in word_sets[1:]:
            common = common.intersection(ws)
        return sorted(common, key=len, reverse=True)
    
    return []


def _suggest_module(functions: List[FunctionSignature]) -> str:
    """Suggest a module name for consolidated functions."""
    # Find common directory
    dirs = [Path(f.file).parent.name for f in functions]
    if len(set(dirs)) == 1:
        return f"{dirs[0]}/utils.py"
    
    # Use first file's directory
    first_dir = Path(functions[0].file).parent
    return str(first_dir / "shared.py")


def generate_recommendations(
    functions: List[FunctionSignature],
    duplicates: List[DuplicateGroup],
) -> List[str]:
    """Generate architecture recommendations.
    
    Args:
        functions: All functions found
        duplicates: Duplicate groups found
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Recommendation based on duplicates
    if duplicates:
        total_savings = sum(g.potential_savings for g in duplicates)
        recommendations.append(
            f"Found {len(duplicates)} group(s) of duplicate code. "
            f"Consolidating could save ~{total_savings} lines."
        )
    
    # Check for functions with same name in different files
    name_to_files: Dict[str, List[str]] = defaultdict(list)
    for func in functions:
        name_to_files[func.name].append(func.file)
    
    for name, files in name_to_files.items():
        if len(files) >= 3 and name not in ('__init__', 'main', 'setup'):
            recommendations.append(
                f"Function '{name}' appears in {len(files)} files. "
                f"Consider if these should be consolidated."
            )
    
    return recommendations


def analyze_project(
    root_path: str,
    min_lines: int = 5,
    similarity_threshold: float = 0.8,
) -> ProjectAnalysis:
    """Analyze an entire project for code patterns.
    
    Args:
        root_path: Root directory to analyze
        min_lines: Minimum function lines to consider
        similarity_threshold: Similarity threshold for duplicates
        
    Returns:
        ProjectAnalysis with findings
    """
    root = Path(root_path)
    analysis = ProjectAnalysis(root_path=root_path)
    
    # Find all Python files
    if root.is_file():
        python_files = [root] if root.suffix == '.py' else []
    else:
        python_files = list(root.rglob("*.py"))
    
    # Extract functions from all files
    all_functions = []
    for file_path in python_files:
        functions = extract_functions_from_file(str(file_path))
        all_functions.extend(functions)
    
    analysis.files_analyzed = len(python_files)
    analysis.functions_found = len(all_functions)
    
    # Find duplicates
    analysis.duplicates = find_duplicates(
        all_functions,
        threshold=similarity_threshold,
        min_lines=min_lines,
    )
    
    # Generate recommendations
    analysis.recommendations = generate_recommendations(
        all_functions,
        analysis.duplicates,
    )
    
    return analysis


def format_project_analysis(analysis: ProjectAnalysis) -> str:
    """Format project analysis for display.
    
    Args:
        analysis: The project analysis result
        
    Returns:
        Formatted string
    """
    lines = []
    
    lines.append("\n" + "=" * 80)
    lines.append("🔍 PROJECT-LEVEL ANALYSIS")
    lines.append("=" * 80)
    lines.append(f"Root: {analysis.root_path}")
    lines.append(f"Files Analyzed: {analysis.files_analyzed}")
    lines.append(f"Functions Found: {analysis.functions_found}")
    lines.append("-" * 80)
    
    if analysis.duplicates:
        lines.append(f"\n🔄 DUPLICATE CODE DETECTED ({len(analysis.duplicates)} groups):")
        lines.append("-" * 40)
        
        for i, group in enumerate(analysis.duplicates, 1):
            lines.append(f"\nGroup {i}: {group.similarity:.0%} Similar ({group.count} functions)")
            for func in group.functions:
                lines.append(f"  • {func.file}:{func.name}() [lines {func.start_line}-{func.end_line}]")
            
            if group.suggested_name:
                lines.append(f"\n  💡 Suggestion: Extract to {group.suggested_module}")
                lines.append(f"     Potential savings: ~{group.potential_savings} lines")
    else:
        lines.append("\n✅ No duplicate code detected!")
    
    if analysis.recommendations:
        lines.append("\n" + "-" * 40)
        lines.append("📊 RECOMMENDATIONS:")
        for rec in analysis.recommendations:
            lines.append(f"  • {rec}")
    
    lines.append("\n" + "=" * 80)
    
    return "\n".join(lines)


def print_project_analysis(analysis: ProjectAnalysis) -> None:
    """Print project analysis to stdout.
    
    Args:
        analysis: The project analysis result
    """
    print(format_project_analysis(analysis))
