#ifndef TORRENTINGSOURCE_H
#define TORRENTINGSOURCE_H
#include <atomic>
#include <functional>
#include <future>
#include <libtorrent/alert_types.hpp>
#include <libtorrent/libtorrent.hpp>
#include <libtorrent/torrent_handle.hpp>
#include <memory>
#include <string>
#include <string_view>
#include <unordered_map>

class TorrentDownloader
{
  public:
    using StateUpdateCallbackT = void(const lt::state_update_alert &);
    lt::session ses{};
    void start_download(std::string_view url, std::string_view filepath);
    TorrentDownloader(const std::function<StateUpdateCallbackT> &callback_on_state_update = nullptr);
    TorrentDownloader(const TorrentDownloader &) = delete;
    TorrentDownloader(const TorrentDownloader &&) = delete;
    void operator=(const TorrentDownloader &) = delete;
    void operator=(const TorrentDownloader &&) = delete;
    ~TorrentDownloader();

  private:
    void process_main_loop();
    using CancellationToken = std::atomic<bool>;
    CancellationToken main_loop_canceller = false;
    std::function<StateUpdateCallbackT> update_callback;
    std::future<void> async_thread;
    std::unordered_map<std::string, lt::torrent_handle *> torrent_info;
};

#endif
