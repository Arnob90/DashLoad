#ifndef ALERTHANDLER_H
#define ALERTHANDLER_H
#include <atomic>
#include <concepts>
#include <functional>
#include <future>
#include <libtorrent/alert.hpp>
#include <libtorrent/alert_types.hpp>
#include <libtorrent/kademlia/types.hpp>
#include <libtorrent/session.hpp>
#include <ranges>
#include <unordered_map>
#include <vector>
namespace torrentdownloader
{
template <typename AlertT>
concept AlertType = std::is_base_of_v<lt::alert, AlertT>;
using AlertTypeRepr = int;
class AlertTypeConnections
{
  public:
    void connect(AlertTypeRepr alert_type, std::function<void(lt::alert *)> callback);
    void execute_connections(lt::alert *sent_alert);

  private:
    std::unordered_map<AlertTypeRepr, std::vector<std::function<void(lt::alert *)>>> connections{};
    std::mutex connections_mutex{};
};
class AlertHandler
{
  public:
    AlertHandler(lt::session &given_session);
    AlertHandler(const AlertHandler &) = delete;
    AlertHandler &operator=(const AlertHandler &) = delete;
    AlertHandler(AlertHandler &&to_move_from) = delete;
    AlertHandler &operator=(AlertHandler &&to_move_from) = delete;

    template <AlertType AlertT>
    void connect(AlertT alert_type, std::function<void(lt::alert *)> callback)
    {
        AlertTypeRepr alert_type_repr = AlertT::type();
        connections.connect(alert_type_repr, callback);
    }

  private:
    void handle_alerts();
    void handle_alerts_main_loop();
    // It is much harder to mess up references than pointers
    lt::session &main_session;
    std::atomic_bool cancellation_flag{false};
    AlertTypeConnections connections{};
    std::future<void> alert_dispatcher_thread;
    ~AlertHandler();
};
} // namespace torrentdownloader
#endif
// namespace alert_handler
