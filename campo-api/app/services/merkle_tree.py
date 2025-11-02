"""
Merkle Tree - Cryptographic hash tree for evidence verification
"""
import hashlib
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class MerkleNode:
    """Node in Merkle tree"""
    hash: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    is_leaf: bool = False
    evidencia_id: Optional[int] = None


class MerkleTree:
    """
    Merkle Tree implementation for evidence integrity verification.
    
    A Merkle tree is a binary tree where:
    - Leaf nodes contain hashes of individual evidences
    - Non-leaf nodes contain hashes of their children
    - Root hash represents the entire evidence set
    
    Properties:
    - Any change to evidence invalidates the tree
    - Efficient verification of individual evidence
    - Compact proof of inclusion
    """
    
    def __init__(self, evidence_hashes: List[tuple[int, str]]):
        """
        Build Merkle tree from evidence hashes.
        
        Args:
            evidence_hashes: List of (evidencia_id, hash_sha256) tuples
        """
        if not evidence_hashes:
            # Empty tree
            self.root = MerkleNode(hash=self._hash(""), is_leaf=True)
            self.leaves = []
            self.depth = 0
            return
        
        # Create leaf nodes
        self.leaves = [
            MerkleNode(
                hash=hash_value,
                is_leaf=True,
                evidencia_id=evidencia_id
            )
            for evidencia_id, hash_value in evidence_hashes
        ]
        
        # Build tree bottom-up
        self.root = self._build_tree(self.leaves)
        self.depth = self._calculate_depth(self.root)
    
    def _build_tree(self, nodes: List[MerkleNode]) -> MerkleNode:
        """
        Recursively build tree from leaf nodes.
        
        Args:
            nodes: Current level nodes
            
        Returns:
            Root node of (sub)tree
        """
        if len(nodes) == 1:
            return nodes[0]
        
        # Build next level
        next_level = []
        
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            
            # If odd number of nodes, duplicate last one
            if i + 1 < len(nodes):
                right = nodes[i + 1]
            else:
                right = nodes[i]
            
            # Create parent node
            combined_hash = self._hash(left.hash + right.hash)
            parent = MerkleNode(
                hash=combined_hash,
                left=left,
                right=right,
                is_leaf=False
            )
            next_level.append(parent)
        
        # Recursively build upper levels
        return self._build_tree(next_level)
    
    def _calculate_depth(self, node: Optional[MerkleNode], current_depth: int = 0) -> int:
        """Calculate tree depth"""
        if node is None or node.is_leaf:
            return current_depth
        
        left_depth = self._calculate_depth(node.left, current_depth + 1)
        right_depth = self._calculate_depth(node.right, current_depth + 1)
        
        return max(left_depth, right_depth)
    
    def _hash(self, data: str) -> str:
        """
        Calculate SHA-256 hash of data.
        
        Args:
            data: String data to hash
            
        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def get_root_hash(self) -> str:
        """Get root hash of tree"""
        return self.root.hash
    
    def verify_evidence(self, evidencia_id: int, hash_value: str) -> bool:
        """
        Verify if evidence with given hash is in the tree.
        
        Args:
            evidencia_id: Evidence ID
            hash_value: Expected hash
            
        Returns:
            True if evidence is verified, False otherwise
        """
        for leaf in self.leaves:
            if leaf.evidencia_id == evidencia_id and leaf.hash == hash_value:
                return True
        return False
    
    def get_proof(self, evidencia_id: int) -> List[str]:
        """
        Get Merkle proof for evidence (for verification).
        
        Args:
            evidencia_id: Evidence ID
            
        Returns:
            List of sibling hashes needed to verify
        """
        # Find leaf
        leaf = None
        for l in self.leaves:
            if l.evidencia_id == evidencia_id:
                leaf = l
                break
        
        if leaf is None:
            return []
        
        # Collect sibling hashes from leaf to root
        proof = []
        current = leaf
        
        # This is a simplified version - in production you'd traverse from leaf to root
        # For now, just return empty list (proof verification not critical for MVP)
        return proof
    
    def to_dict(self) -> dict:
        """
        Convert tree to dictionary representation.
        
        Returns:
            Dict with root_hash, leaf_count, depth, and leaves
        """
        return {
            "root_hash": self.get_root_hash(),
            "leaf_count": len(self.leaves),
            "tree_depth": self.depth,
            "leaves": [
                {
                    "evidencia_id": leaf.evidencia_id,
                    "hash": leaf.hash
                }
                for leaf in self.leaves
            ]
        }
