Binary search misses the final remaining candidate because the loop stops while
`left == right`. Repair the boundary condition so the last position is checked.
