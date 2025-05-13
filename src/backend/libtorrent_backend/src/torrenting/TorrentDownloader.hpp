#ifndef TORRENT_DOWNLOADER_H
#define TORRENT_DOWNLOADER_H
#include "AlertHandler.hpp"
#include <libtorrent/add_torrent_params.hpp>
#include <libtorrent/magnet_uri.hpp>
#include <libtorrent/session.hpp>
#include <libtorrent/string_view.hpp>
#include <libtorrent/torrent_handle.hpp>
#include <string_view>
#include <unordered_map>
namespace torrentdownloader
{
libtorrent::string_view convert_str_view_to_boost_view(std::string_view given_view);
class TorrentDownloader
{
  public:
    void start_download(std::string_view magnet_link, std::string_view filepath_to_save_in);
    void pause_download(std::string_view id_to_pause);
    void cancel_download(std::string_view id_to_pause);

  private:
    static lt::session main_session;
    std::unordered_map<std::string, lt::torrent_handle> id_to_downloads;
    AlertHandler alert_handler{main_session};
    void handle_torrent_added_callback(lt::torrent_handle handle);
    void handle_alerts();
};
} // namespace torrentdownloader
#endif // TORRENT_DOWNLOADER_H
