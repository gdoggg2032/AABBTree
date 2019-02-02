import copy

__all__ = ['AABB', 'AABBTree']
__author__ = 'Kenneth (Kip) Hart'


class AABB(object):
    """Axis aligned bounding box (AABB)

    The AABB is a d-dimensional box.

    Args:
        limits (iterable, optional): The limits of the box. These should be
            specified in the following manner::

                limits = [(xmin, xmax),
                          (ymin, ymax),
                          (zmin, zmax),
                          ...]

            The default value is None.
    """
    def __init__(self, limits=None):
        if limits is not None:
            for lims in limits:
                assert len(lims) == 2
                assert lims[0] <= lims[1]

        self.limits = limits
        self._i = 0

    def __str__(self):
        return str(self.limits)

    def __repr__(self):
        return 'AABB(' + repr(self.limits) + ')'

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i < len(self):
            val = self.limits[self._i]
            self._i += 1
            return val
        raise StopIteration

    def next(self):  # pragma: no cover
        """___next__ for Python 2"""
        return self.__next__()

    def __getitem__(self, key):
        return self.limits[key]

    def __len__(self):
        return len(self.limits)

    def __eq__(self, aabb):
        if not isinstance(aabb, AABB):
            return False

        if (self.limits is None) and (aabb.limits is None):
            return True
        if (self.limits is None) or (aabb.limits is None):
            return False
        if len(self) != len(aabb):
            return False

        for i, lims1 in enumerate(self):
            lims2 = aabb[i]
            if (lims1[0] != lims2[0]) or (lims1[1] != lims2[1]):
                return False
        return True

    def __ne__(self, aabb):
        return not self.__eq__(aabb)

    @classmethod
    def merge(cls, aabb1, aabb2):
        """Merge AABB

        Find the AABB of the union of AABBs.

        Args:
            aabb1 (AABB): An AABB
            aabb2 (AABB): An AABB

        Returns:
            AABB: An AABB that contains both of the inputs
        """
        if (aabb1.limits is None) and (aabb2.limits is None):
            return cls(None)
        if aabb1.limits is None:
            return cls(aabb2.limits)
        if aabb2.limits is None:
            return cls(aabb1.limits)

        merged_limits = []
        for lims1, lims2 in zip(aabb1, aabb2):
            lower = min(lims1[0], lims2[0])
            upper = max(lims1[1], lims2[1])
            merged_limits.append((lower, upper))
        return cls(merged_limits)

    @property
    def perimeter(self):
        r"""float: perimeter of AABB

        The perimeter :math:`p_n` of an AABB with side lengths
        :math:`l_1 \ldots l_n` is:

        .. math::

            p_1 &= 0 \\
            p_2 &= 2 (l_1 + l_2) \\
            p_3 &= 2 (l_1 l_2 + l_2 l_3 + l_1 l_3) \\
            p_n &= 2 \sum_{i=1}^n \prod_{j=1\neq i}^n l_j

        """
        if len(self) == 1:
            return 0

        perim = 0
        side_lens = [ub - lb for lb, ub in self]
        n_dim = len(side_lens)
        for i in range(n_dim):
            p_edge = 1
            for j in range(n_dim):
                if j != i:
                    p_edge *= side_lens[j]
            perim += p_edge
        return 2 * perim

    @property
    def volume(self):
        """float: volume of AABB"""
        vol = 1
        for lb, ub in self:
            vol *= ub - lb
        return vol

    def overlaps(self, aabb):
        """Determine if two AABBs overlap

        Args:
            aabb (AABB): The AABB to check for overlap

        Returns:
            bool: Flag set to true if the two AABBs overlap
        """
        if (self.limits is None) or (aabb.limits is None):
            return False

        for lims1, lims2 in zip(self, aabb):
            min1, max1 = lims1
            min2, max2 = lims2

            overlaps = (max1 >= min2) and (min1 <= max2)
            if not overlaps:
                return False
        return True

    def overlap_volume(self, aabb):
        r"""Determine volume of overlap between AABBs

        Let :math:`(x_i^l, x_i^u)` be the i-th dimension
        lower and upper bounds for AABB 1, and
        let :math:`(y_i^l, y_i^u)` be the lower and upper bounds for
        AABB 2. The volume of overlap is:

        .. math::

            V = \prod_{i=1}^n \text{max}(0, \text{min}(x_i^u, y_i^u) - \text{max}(x_i^l, y_i^l))

        Args:
            aabb (AABB): The AABB to calculate for overlap volume

        Returns:
            float: Volume of overlap
        """  # NOQA: E501

        volume = 1
        for lims1, lims2 in zip(self, aabb):
            min1, max1 = lims1
            min2, max2 = lims2

            overlap_min = max(min1, min2)
            overlap_max = min(max1, max2)
            if overlap_min >= overlap_max:
                return 0

            volume *= overlap_max - overlap_min
        return volume


class AABBTree(object):
    """Python Implementation of the AABB Tree

    This is a pure Python implementation of the static d-dimensional AABB tree.
    It is heavily based on
    `Introductory Guide to AABB Tree Collision Detection`_
    from *Azure From The Trenches*.

    Args:
        aabb (AABB): An AABB
        value: The value associated with the AABB
        left (AABBTree, optional): The left branch of the tree
        right (AABBTree, optional): The right branch of the tree

    .. _`Introductory Guide to AABB Tree Collision Detection` : https://www.azurefromthetrenches.com/introductory-guide-to-aabb-tree-collision-detection/
    """  # NOQA: E501
    def __init__(self, aabb=AABB(), value=None, left=None, right=None):

        self.aabb = aabb
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        inp_strs = []
        if self.aabb != AABB():
            inp_strs.append('aabb=' + repr(self.aabb))

        if self.value is not None:
            inp_strs.append('value=' + repr(self.value))

        if self.left is not None:
            inp_strs.append('left=' + repr(self.left))

        if self.right is not None:
            inp_strs.append('right=' + repr(self.right))

        return 'AABBTree(' + ', '.join(inp_strs) + ')'

    def __str__(self, n=0):
        pre = n * '  '

        aabb_str = pre + 'AABB: '
        if self.aabb == AABB():
            aabb_str += 'None'
        else:
            aabb_str += str(self.aabb)

        value_str = pre + 'Value: ' + str(self.value)

        left_str = pre + 'Left:'
        if self.left is None:
            left_str += ' None'
        else:
            left_str += '\n' + self.left.__str__(n + 1)

        right_str = pre + 'Right:'
        if self.right is None:
            right_str += ' None'
        else:
            right_str += '\n' + self.right.__str__(n + 1)

        return '\n'.join([aabb_str, value_str, left_str, right_str])

    def __eq__(self, aabbtree):
        if not isinstance(aabbtree, AABBTree):
            return False

        if self.aabb != aabbtree.aabb:
            return False

        if self.is_leaf != aabbtree.is_leaf:
            return False

        return (self.left == aabbtree.left) and (self.right == aabbtree.right)

    def __ne__(self, aabbtree):
        return not self.__eq__(aabbtree)

    def __len__(self):
        if self.is_leaf:
            return int(self.aabb != AABB())
        else:
            return len(self.left) + len(self.right)

    @property
    def is_leaf(self):
        """bool: returns True if is leaf node"""
        return (self.left is None) and (self.right is None)

    @property
    def depth(self):
        """int: Depth of the tree"""
        if self.is_leaf:
            return 0
        else:
            return 1 + max(self.left.depth, self.right.depth)

    def add(self, aabb, value=None, method='volume'):
        r"""Add node to tree

        This function inserts a node into the AABB tree.
        The function chooses one of three options for adding the node to
        the tree:

            * Add it to the left side
            * Add it to the right side
            * Become a leaf node

        The cost of each option is calculated based on the *method* keyword,
        and the option with the lowest cost is chosen.

        Args:
            aabb (AABB): The AABB to add.
            value: The value associated with the AABB. Defaults to None.
            method (str): The method for deciding how to build the tree.
                Should be one of the following:

                    * 'volume'

                **'volume'**
                *Costs based on total bounding volume and overlap volume*

                Let :math:`b` denote the tree, :math:`l` denote the left
                branch, :math:`r` denote the right branch, :math:`x` denote
                the AABB to add, and math:`V` be the volume of an AABB.
                The cost associated with each of these options is:

                .. math::

                    C(\text{add left})  &= V(b \cup x) - V(b) + V(l \cup x) - V(l) + V((l \cup x) \cap r) \\
                    C(\text{add right}) &= V(b \cup x) - V(b) + V(r \cup x) - V(r) + V((r \cup x) \cap l) \\
                    C(\text{leaf})      &= V(b \cup x) + V(b \cap x)

                The first two terms in the 'add left' cost represent the change
                in volume for the tree. The next two terms give the change in
                volume for the left branch specifically (right branch is
                unchanged). The final term is the amount of overlap that would
                be between the new left branch and the right branch.

                This cost function includes the increases in bounding volumes and
                the amount of overlap- two values a balanced AABB tree should minimize.

                The 'add right' cost is a mirror opposite of the 'add left cost'.
                The 'leaf' cost is the added bounding volume plus a penalty for
                overlapping with the existing tree.

                These costs suit the author's current needs.
                Other applications, such as raytracing, are more concerned
                with surface area than volume. Please visit the
                `AABBTree repository`_ if you are interested in implementing
                another cost function.

        .. _`AABBTree repository`: https://github.com/kip-hart/AABBTree

        """  # NOQA: E501
        if self.aabb == AABB():
            self.aabb = aabb
            self.value = value

        elif self.is_leaf:
            self.left = copy.deepcopy(self)
            self.right = AABBTree(aabb, value)

            self.aabb = AABB.merge(self.aabb, aabb)
            self.value = None
        else:
            if method == 'volume':
                # Define merged AABBs
                branch_merge = AABB.merge(self.aabb, aabb)
                left_merge = AABB.merge(self.left.aabb, aabb)
                right_merge = AABB.merge(self.right.aabb, aabb)

                # Calculate the change in the sum of the bounding volumes
                branch_bnd_cost = branch_merge.volume

                left_bnd_cost = branch_merge.volume - self.aabb.volume
                left_bnd_cost += left_merge.volume - self.left.aabb.volume

                right_bnd_cost = branch_merge.volume - self.aabb.volume
                right_bnd_cost += right_merge.volume - self.right.aabb.volume

                # Calculate amount of overlap
                branch_olap_cost = self.aabb.overlap_volume(aabb)
                left_olap_cost = left_merge.overlap_volume(self.right.aabb)
                right_olap_cost = right_merge.overlap_volume(self.left.aabb)

                # Calculate total cost
                branch_cost = branch_bnd_cost + branch_olap_cost
                left_cost = left_bnd_cost + left_olap_cost
                right_cost = right_bnd_cost + right_olap_cost
            else:
                raise ValueError('Unrecognized method: ' + str(method))

            if branch_cost < left_cost and branch_cost < right_cost:
                self.left = copy.deepcopy(self)
                self.right = AABBTree(aabb, value)
                self.value = None
            elif left_cost < right_cost:
                self.left.add(aabb, value)
            else:
                self.right.add(aabb, value)
            self.aabb = AABB.merge(self.left.aabb, self.right.aabb)

    def does_overlap(self, aabb):
        """Check for overlap

        This function checks if the limits overlap any leaf nodes in the tree.
        It returns true if there is an overlap.

        Args:
            aabb (AABB): The AABB to check.

        Returns:
            bool: True if overlaps with a leaf node of tree.
        """
        if self.is_leaf:
            return self.aabb.overlaps(aabb)

        left_aabb_over = self.left.aabb.overlaps(aabb)
        right_aabb_over = self.right.aabb.overlaps(aabb)

        if left_aabb_over and self.left.does_overlap(aabb):
            return True
        if right_aabb_over and self.right.does_overlap(aabb):
            return True
        return False

    def overlap_values(self, aabb):
        """Get values of overlapping AABBs

        This function gets the value field of each overlapping AABB.

        Args:
            aabb (AABB): The AABB to check.

        Returns:
            list: Value fields of each node that overlaps.
        """
        values = []
        if self.is_leaf and self.does_overlap(aabb):
            values.append(self.value)
        elif self.is_leaf:
            pass
        else:
            if self.left.aabb.overlaps(aabb):
                values.extend(self.left.overlap_values(aabb))

            if self.right.aabb.overlaps(aabb):
                values.extend(self.right.overlap_values(aabb))
        return values
