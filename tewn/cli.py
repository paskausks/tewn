import click
from tewn import audio


@click.command()
def main(args=None):
    """Console script for tewn."""
    mic = None

    try:
        mic = audio.MicrophoneInput()
    except audio.MicrophoneInputException as e:
        click.echo(str(e), err=True)
        exit(1)

    click.secho(
        'Input initialized. Ready to listen on %s.' % mic.device_name,
        fg='green'
    )

    mic.listen()
    mic.quit()


if __name__ == "__main__":
    main()
