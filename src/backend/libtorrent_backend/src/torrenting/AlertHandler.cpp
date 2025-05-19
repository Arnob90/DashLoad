#include "AlertHandler.hpp"
#include "TorrentDownloader.hpp"
#include <future>
#include <libtorrent/alert.hpp>
#include <libtorrent/alert_types.hpp>
#include <libtorrent/settings_pack.hpp>
#include <mutex>
#include <vector>

namespace torrentdownloader
{
// AlertTypeConnections definitions
void AlertTypeConnections::connect(AlertTypeRepr alert_type, std::function<void(lt::alert *)> callback)
{
    std::lock_guard<std::mutex> lock(connections_mutex);
    if (connections.find(alert_type) == connections.end())
    {
        connections[alert_type] = std::vector<std::function<void(lt::alert *)>>();
    }
    connections[alert_type].push_back(callback);
}
void AlertTypeConnections::execute_connections(lt::alert *sent_alert)
{
    const AlertTypeRepr alert_type = sent_alert->type();
    std::lock_guard<std::mutex> lock(connections_mutex);
    if (connections.find(alert_type) != connections.end())
    {
        for (const auto &connection : connections[alert_type])
        {
            connection(sent_alert);
        }
    }
}
// AlertHandler definitions
void AlertHandler::handle_alerts()
{
    std::vector<lt::alert *> alerts;
    // Populate the vec
    main_session.pop_alerts(&alerts);

    for (lt::alert *alert : alerts)
    {
        connections.execute_connections(alert);
    }
}
void AlertHandler::handle_alerts_main_loop()
{
    while (!cancellation_flag)
    {
        handle_alerts();
    }
}
AlertHandler::AlertHandler(lt::session &given_session) : main_session(given_session)
{
    alert_dispatcher_thread = std::async(&AlertHandler::handle_alerts_main_loop, this);
}
AlertHandler::~AlertHandler()
{
    cancellation_flag.store(true);
    // wait till it's safe to destroy
    alert_dispatcher_thread.wait();
}
} // namespace torrentdownloader
