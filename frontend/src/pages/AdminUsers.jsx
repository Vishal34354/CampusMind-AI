import { useCallback, useEffect, useState } from "react";
import "./AdminUsers.css";

function AdminUsers({ currentUser, onNavigateBack }) {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [pages, setPages] = useState(1);

  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Modals
  const [selectedUser, setSelectedUser] = useState(null);
  const [confirmUser, setConfirmUser] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [modalError, setModalError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("access_token");
      const queryParams = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      });

      if (search.trim()) {
        queryParams.append("search", search.trim());
      }

      if (statusFilter && statusFilter !== "all") {
        queryParams.append("status_filter", statusFilter);
      }

      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/admin/users?${queryParams.toString()}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to fetch user accounts"
        );
      }

      setUsers(data.items || []);
      setTotal(data.total || 0);
      setPages(data.pages || 1);
    } catch (err) {
      console.error("Error fetching admin users:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [page, limit, search, statusFilter]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  const handleClearSearch = () => {
    setSearchInput("");
    setSearch("");
    setPage(1);
  };

  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
    setPage(1);
  };

  const handleToggleStatus = async () => {
    if (!confirmUser) return;

    setActionLoading(true);
    setModalError("");

    try {
      const token = localStorage.getItem("access_token");
      const nextStatus = !confirmUser.is_active;

      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/admin/users/${confirmUser.id}/status`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            is_active: nextStatus,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Failed to update user account status"
        );
      }

      setSuccessMessage(
        `Successfully ${nextStatus ? "activated" : "deactivated"} account for ${confirmUser.full_name}.`
      );

      setConfirmUser(null);
      await fetchUsers();

      setTimeout(() => {
        setSuccessMessage("");
      }, 4000);
    } catch (err) {
      console.error("Status update error:", err);
      setModalError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Stats calculation
  const activeCount = users.filter((u) => u.is_active).length;
  const adminCount = users.filter((u) => u.is_admin || u.role === "admin").length;

  return (
    <div className="admin-page">
      {/* Page Header */}
      <div className="admin-header">
        <div>
          <div className="admin-badge-header">Administrator Dashboard</div>
          <h1>User Account Management</h1>
          <p>
            View all registered users, monitor study activity, and manage account statuses.
          </p>
        </div>

        {onNavigateBack && (
          <button className="back-button" onClick={onNavigateBack}>
            &larr; Back to Study Dashboard
          </button>
        )}
      </div>

      {/* Stats Cards */}
      <div className="admin-stats-grid">
        <div className="stat-card">
          <div className="stat-title">Total Users</div>
          <div className="stat-value">{total}</div>
          <div className="stat-desc">Registered in database</div>
        </div>

        <div className="stat-card">
          <div className="stat-title">Active Page View</div>
          <div className="stat-value">{activeCount}</div>
          <div className="stat-desc">Users active on current page</div>
        </div>

        <div className="stat-card">
          <div className="stat-title">Administrators</div>
          <div className="stat-value">{adminCount}</div>
          <div className="stat-desc">Privileged accounts</div>
        </div>
      </div>

      {/* Success Notification */}
      {successMessage && (
        <div className="admin-alert success-alert" role="alert">
          <span>✓ {successMessage}</span>
          <button onClick={() => setSuccessMessage("")}>&times;</button>
        </div>
      )}

      {/* Error Notification */}
      {error && (
        <div className="admin-alert error-alert" role="alert">
          <span>⚠️ {error}</span>
          <button onClick={fetchUsers}>Retry</button>
        </div>
      )}

      {/* Controls: Search and Filters */}
      <div className="admin-controls-card">
        <form onSubmit={handleSearchSubmit} className="search-form">
          <div className="search-input-wrapper">
            <svg
              className="search-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              placeholder="Search users by name or email..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              aria-label="Search users by name or email"
            />
            {searchInput && (
              <button
                type="button"
                className="clear-search"
                onClick={handleClearSearch}
                aria-label="Clear search"
              >
                &times;
              </button>
            )}
          </div>
          <button type="submit" className="search-button">
            Search
          </button>
        </form>

        <div className="filter-wrapper">
          <label htmlFor="status-filter-select">Status Filter:</label>
          <select
            id="status-filter-select"
            value={statusFilter}
            onChange={handleStatusFilterChange}
          >
            <option value="all">All Accounts</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
          </select>

          <button
            className="refresh-button"
            onClick={fetchUsers}
            title="Refresh user list"
            disabled={loading}
          >
            🔄 {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {/* Table Container */}
      <div className="table-card">
        {loading ? (
          <div className="admin-loading-state">
            <div className="spinner"></div>
            <p>Fetching user accounts from PostgreSQL...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="admin-empty-state">
            <h3>No users found</h3>
            <p>
              {search || statusFilter !== "all"
                ? "No registered users match your search criteria."
                : "There are currently no registered users in the database."}
            </p>
            {(search || statusFilter !== "all") && (
              <button
                className="clear-filters-button"
                onClick={() => {
                  setSearchInput("");
                  setSearch("");
                  setStatusFilter("all");
                  setPage(1);
                }}
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <div className="table-responsive">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>User Details</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Study Materials</th>
                  <th>Registered Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => {
                  const isAdmin = user.is_admin || user.role === "admin";
                  const isCurrentLoggedUser =
                    currentUser && currentUser.id === user.id;

                  return (
                    <tr key={user.id} className={!user.is_active ? "inactive-row" : ""}>
                      <td>
                        <div className="user-info-cell">
                          <div className="avatar-circle">
                            {user.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
                          </div>
                          <div>
                            <div className="user-name">
                              {user.full_name}
                              {isCurrentLoggedUser && (
                                <span className="you-badge">(You)</span>
                              )}
                            </div>
                            <div className="user-email">{user.email}</div>
                          </div>
                        </div>
                      </td>

                      <td>
                        <span
                          className={`role-badge ${isAdmin ? "role-admin" : "role-user"}`}
                        >
                          {isAdmin ? "👑 Administrator" : "🎓 Student"}
                        </span>
                      </td>

                      <td>
                        <span
                          className={`status-badge ${user.is_active ? "status-active" : "status-inactive"}`}
                        >
                          <span className="status-dot"></span>
                          {user.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>

                      <td>
                        <span className="materials-count-pill">
                          📚 {user.materials_count || 0}{" "}
                          {user.materials_count === 1 ? "File" : "Files"}
                        </span>
                      </td>

                      <td className="date-cell">{formatDate(user.created_at)}</td>

                      <td>
                        <div className="action-buttons">
                          <button
                            className="btn-action btn-details"
                            onClick={() => setSelectedUser(user)}
                            title="View safe user details"
                          >
                            Details
                          </button>

                          <button
                            className={`btn-action ${user.is_active ? "btn-deactivate" : "btn-activate"}`}
                            onClick={() => {
                              setConfirmUser(user);
                              setModalError("");
                            }}
                            title={
                              isCurrentLoggedUser && user.is_active
                                ? "You cannot deactivate your own account"
                                : user.is_active
                                ? "Deactivate account"
                                : "Activate account"
                            }
                          >
                            {user.is_active ? "Deactivate" : "Activate"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        {!loading && users.length > 0 && (
          <div className="admin-pagination">
            <div className="pagination-info">
              Showing page <strong>{page}</strong> of <strong>{pages}</strong> ({total}{" "}
              total registered users)
            </div>

            <div className="pagination-controls">
              <button
                className="btn-page"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
              >
                &laquo; Previous
              </button>

              <span className="page-number-display">
                {page} / {pages}
              </span>

              <button
                className="btn-page"
                onClick={() => setPage((p) => Math.min(pages, p + 1))}
                disabled={page >= pages}
              >
                Next &raquo;
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ================= USER DETAILS MODAL ================= */}
      {selectedUser && (
        <div className="modal-backdrop" onClick={() => setSelectedUser(null)}>
          <div
            className="modal-content glass-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-labelledby="user-detail-title"
          >
            <div className="modal-header">
              <h2 id="user-detail-title">User Account Details</h2>
              <button
                className="modal-close-btn"
                onClick={() => setSelectedUser(null)}
                aria-label="Close modal"
              >
                &times;
              </button>
            </div>

            <div className="modal-body">
              <div className="detail-user-card">
                <div className="avatar-large">
                  {selectedUser.full_name
                    ? selectedUser.full_name.charAt(0).toUpperCase()
                    : "U"}
                </div>
                <div>
                  <h3>{selectedUser.full_name}</h3>
                  <p>{selectedUser.email}</p>
                </div>
              </div>

              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">User ID (UUID):</span>
                  <span className="detail-value code-font">{selectedUser.id}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Assigned Role:</span>
                  <span className="detail-value">
                    {selectedUser.is_admin || selectedUser.role === "admin"
                      ? "Administrator"
                      : "Student / Standard User"}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Account Status:</span>
                  <span className="detail-value">
                    {selectedUser.is_active ? "Active" : "Inactive"}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Uploaded Study Materials:</span>
                  <span className="detail-value">
                    {selectedUser.materials_count || 0} document(s)
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Registration Date:</span>
                  <span className="detail-value">
                    {formatDate(selectedUser.created_at)}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">Last Updated:</span>
                  <span className="detail-value">
                    {formatDate(selectedUser.updated_at)}
                  </span>
                </div>
              </div>

              <div className="security-notice">
                🔒 <strong>Security Policy:</strong> Password hashes, secrets, and authorization tokens are strictly protected and never displayed in the application interface.
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn-modal-close"
                onClick={() => setSelectedUser(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= CONFIRMATION MODAL ================= */}
      {confirmUser && (
        <div className="modal-backdrop" onClick={() => setConfirmUser(null)}>
          <div
            className="modal-content confirm-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-labelledby="confirm-modal-title"
          >
            <div className="modal-header">
              <h2 id="confirm-modal-title">
                {confirmUser.is_active ? "Deactivate User Account?" : "Activate User Account?"}
              </h2>
              <button
                className="modal-close-btn"
                onClick={() => setConfirmUser(null)}
                disabled={actionLoading}
              >
                &times;
              </button>
            </div>

            <div className="modal-body">
              <p>
                Are you sure you want to{" "}
                <strong>
                  {confirmUser.is_active ? "deactivate" : "activate"}
                </strong>{" "}
                the account for <strong>{confirmUser.full_name}</strong> (
                {confirmUser.email})?
              </p>

              {confirmUser.is_active && (
                <div className="warning-box">
                  ⚠️ Deactivating this account will prevent the user from logging in to CampusMind AI until reactivated by an administrator.
                </div>
              )}

              {modalError && (
                <div className="admin-alert error-alert">
                  <span>⚠️ {modalError}</span>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn-cancel"
                onClick={() => setConfirmUser(null)}
                disabled={actionLoading}
              >
                Cancel
              </button>

              <button
                className={`btn-confirm ${confirmUser.is_active ? "btn-confirm-danger" : "btn-confirm-success"}`}
                onClick={handleToggleStatus}
                disabled={actionLoading}
              >
                {actionLoading
                  ? "Updating..."
                  : confirmUser.is_active
                  ? "Yes, Deactivate"
                  : "Yes, Activate"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminUsers;
