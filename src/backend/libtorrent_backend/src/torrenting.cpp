#include "torrenting.hpp"
#include <chrono>
#include <future>
#include <libtorrent/alert.hpp>
#include <libtorrent/alert_types.hpp>
#include <libtorrent/libtorrent.hpp>
#include <libtorrent/magnet_uri.hpp>
#include <libtorrent/torrent_handle.hpp>
#include <memory>
#include <string_view>
#include <thread>
#include <unistd.h>
#include <vector>

TorrentDownloader::TorrentDownloader(const std::function<StateUpdateCallbackT> &callback_on_state_update) : update_callback(callback_on_state_update)
{
    async_thread = std::async(std::launch::async, &TorrentDownloader::process_main_loop, this);
}

void TorrentDownloader::start_download(std::string_view url, std::string_view filepath)
{
    auto params = lt::parse_magnet_uri(std::string(url));
    params.save_path = filepath;
    auto handle = ses.add_torrent(std::move(params));
}

void TorrentDownloader::process_main_loop()
{
    while (main_loop_canceller.load() == false)
    {
        ses.post_torrent_updates();
        std::vector<lt::alert *> alerts;
        // Load all alerts
        ses.pop_alerts(&alerts);
        for (const auto &alert : alerts)
        {
            auto update_alert = lt::alert_cast<lt::state_update_alert>(alert);
            if (update_alert && update_callback)
            {
                update_callback(*update_alert);
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

TorrentDownloader::~TorrentDownloader()
{
    main_loop_canceller.store(true);
    // Block until the thread is gone for safety reasons
    async_thread.get();
}
